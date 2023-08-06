"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var base = require("./base");
var logging_1 = require("./core/logging");
var document_1 = require("./document");
var dom_1 = require("./core/dom");
var callback_1 = require("./core/util/callback");
var string_1 = require("./core/util/string");
var object_1 = require("./core/util/object");
var types_1 = require("./core/util/types");
var receiver_1 = require("./protocol/receiver");
var connection_1 = require("./client/connection");
exports.kernels = {};
// Matches Bokeh CSS class selector. Setting all Bokeh parent element class names
// with this var prevents user configurations where css styling is unset.
exports.BOKEH_ROOT = "bk-root";
function _handle_notebook_comms(receiver, comm_msg) {
    if (comm_msg.buffers.length > 0)
        receiver.consume(comm_msg.buffers[0].buffer);
    else
        receiver.consume(comm_msg.content.data);
    var msg = receiver.message;
    if (msg != null)
        this.apply_json_patch(msg.content, msg.buffers);
}
function _init_comms(target, doc) {
    if (typeof Jupyter !== 'undefined' && Jupyter.notebook.kernel != null) {
        logging_1.logger.info("Registering Jupyter comms for target " + target);
        var comm_manager = Jupyter.notebook.kernel.comm_manager;
        try {
            comm_manager.register_target(target, function (comm) {
                logging_1.logger.info("Registering Jupyter comms for target " + target);
                var r = new receiver_1.Receiver();
                comm.on_msg(_handle_notebook_comms.bind(doc, r));
            });
        }
        catch (e) {
            logging_1.logger.warn("Jupyter comms failed to register. push_notebook() will not function. (exception reported: " + e + ")");
        }
    }
    else if (doc.roots()[0].id in exports.kernels) {
        logging_1.logger.info("Registering JupyterLab comms for target " + target);
        var kernel = exports.kernels[doc.roots()[0].id];
        try {
            kernel.registerCommTarget(target, function (comm) {
                logging_1.logger.info("Registering JupyterLab comms for target " + target);
                var r = new receiver_1.Receiver();
                comm.onMsg = _handle_notebook_comms.bind(doc, r);
            });
        }
        catch (e) {
            logging_1.logger.warn("Jupyter comms failed to register. push_notebook() will not function. (exception reported: " + e + ")");
        }
    }
    else {
        console.warn("Jupyter notebooks comms not available. push_notebook() will not function. If running JupyterLab ensure the latest jupyterlab_bokeh extension is installed. In an exported notebook this warning is expected.");
    }
}
function _create_view(model) {
    var view = new model.default_view({ model: model, parent: null });
    base.index[model.id] = view;
    return view;
}
function _get_element(item) {
    var element_id = item.elementid;
    var elem = document.getElementById(element_id);
    if (elem == null)
        throw new Error("Error rendering Bokeh model: could not find tag with id: " + element_id);
    if (!document.body.contains(elem))
        throw new Error("Error rendering Bokeh model: element with id '" + element_id + "' must be under <body>");
    // if autoload script, replace script tag with div for embedding
    if (elem.tagName == "SCRIPT") {
        fill_render_item_from_script_tag(elem, item);
        var container = dom_1.div({ class: exports.BOKEH_ROOT });
        dom_1.replaceWith(elem, container);
        var child = dom_1.div();
        container.appendChild(child);
        elem = child;
    }
    return elem;
}
// Replace element with a view of model_id from document
function add_model_standalone(model_id, element, doc) {
    var model = doc.get_model_by_id(model_id);
    if (model == null)
        throw new Error("Model " + model_id + " was not in document " + doc);
    var view = _create_view(model);
    view.renderTo(element, true);
    return view;
}
exports.add_model_standalone = add_model_standalone;
// Fill element with the roots from doc
function add_document_standalone(document, element, use_for_title) {
    if (use_for_title === void 0) { use_for_title = false; }
    // this is a LOCAL index of views used only by this particular rendering
    // call, so we can remove the views we create.
    var views = {};
    function render_model(model) {
        var view = _create_view(model);
        view.renderTo(element);
        views[model.id] = view;
    }
    function unrender_model(model) {
        if (model.id in views) {
            var view = views[model.id];
            element.removeChild(view.el);
            delete views[model.id];
            delete base.index[model.id];
        }
    }
    for (var _i = 0, _a = document.roots(); _i < _a.length; _i++) {
        var model = _a[_i];
        render_model(model);
    }
    if (use_for_title)
        window.document.title = document.title();
    document.on_change(function (event) {
        if (event instanceof document_1.RootAddedEvent)
            render_model(event.model);
        else if (event instanceof document_1.RootRemovedEvent)
            unrender_model(event.model);
        else if (use_for_title && event instanceof document_1.TitleChangedEvent)
            window.document.title = event.title;
    });
    return views;
}
exports.add_document_standalone = add_document_standalone;
// map { websocket url to map { session id to promise of ClientSession } }
var _sessions = {};
function _get_session(websocket_url, session_id, args_string) {
    if (!(websocket_url in _sessions))
        _sessions[websocket_url] = {};
    var subsessions = _sessions[websocket_url];
    if (!(session_id in subsessions))
        subsessions[session_id] = connection_1.pull_session(websocket_url, session_id, args_string);
    return subsessions[session_id];
}
// Fill element with the roots from session_id
function add_document_from_session(element, websocket_url, session_id, use_for_title) {
    var args_string = window.location.search.substr(1);
    var promise = _get_session(websocket_url, session_id, args_string);
    return promise.then(function (session) {
        return add_document_standalone(session.document, element, use_for_title);
    }, function (error) {
        logging_1.logger.error("Failed to load Bokeh session " + session_id + ": " + error);
        throw error;
    });
}
exports.add_document_from_session = add_document_from_session;
// Replace element with a view of model_id from the given session
function add_model_from_session(element, websocket_url, model_id, session_id) {
    var args_string = window.location.search.substr(1);
    var promise = _get_session(websocket_url, session_id, args_string);
    return promise.then(function (session) {
        var model = session.document.get_model_by_id(model_id);
        if (model == null)
            throw new Error("Did not find model " + model_id + " in session");
        var view = _create_view(model);
        view.renderTo(element, true);
        return view;
    }, function (error) {
        logging_1.logger.error("Failed to load Bokeh session " + session_id + ": " + error);
        throw error;
    });
}
exports.add_model_from_session = add_model_from_session;
function inject_css(url) {
    var element = dom_1.link({ href: url, rel: "stylesheet", type: "text/css" });
    document.body.appendChild(element);
}
exports.inject_css = inject_css;
function inject_raw_css(css) {
    var element = dom_1.style({}, css);
    document.body.appendChild(element);
}
exports.inject_raw_css = inject_raw_css;
// pull missing render item fields from data- attributes
function fill_render_item_from_script_tag(script, item) {
    var _a = script.dataset, bokehLogLevel = _a.bokehLogLevel, bokehDocId = _a.bokehDocId, bokehModelId = _a.bokehModelId, bokehSessionId = _a.bokehSessionId;
    // length checks are because we put all the attributes on the tag
    // but sometimes set them to empty string
    if (bokehLogLevel != null && bokehLogLevel.length > 0)
        logging_1.set_log_level(bokehLogLevel);
    if (bokehDocId != null && bokehDocId.length > 0)
        item.docid = bokehDocId;
    if (bokehModelId != null && bokehModelId.length > 0)
        item.modelid = bokehModelId;
    if (bokehSessionId != null && bokehSessionId.length > 0)
        item.sessionid = bokehSessionId;
    logging_1.logger.info("Will inject Bokeh script tag with params " + JSON.stringify(item));
}
function embed_items_notebook(docs_json, render_items) {
    if (object_1.size(docs_json) != 1)
        throw new Error("embed_items_notebook expects exactly one document in docs_json");
    var doc = document_1.Document.from_json(object_1.values(docs_json)[0]);
    for (var _i = 0, render_items_1 = render_items; _i < render_items_1.length; _i++) {
        var item = render_items_1[_i];
        if (item.notebook_comms_target != null)
            _init_comms(item.notebook_comms_target, doc);
        var elem = _get_element(item);
        if (item.modelid != null)
            add_model_standalone(item.modelid, elem, doc);
        else
            add_document_standalone(doc, elem, false);
    }
}
exports.embed_items_notebook = embed_items_notebook;
function _get_ws_url(app_path, absolute_url) {
    var protocol = 'ws:';
    if (window.location.protocol == 'https:')
        protocol = 'wss:';
    var loc;
    if (absolute_url != null) {
        loc = document.createElement('a');
        loc.href = absolute_url;
    }
    else
        loc = window.location;
    if (app_path != null) {
        if (app_path == "/")
            app_path = "";
    }
    else
        app_path = loc.pathname.replace(/\/+$/, '');
    return protocol + '//' + loc.host + app_path + '/ws';
}
// TODO (bev) this is currently clunky. Standalone embeds only provide
// the first two args, whereas server provide the app_app, and *may* prove and
// absolute_url as well if non-relative links are needed for resources. This function
// should probably be split in to two pieces to reflect the different usage patterns
function embed_items(docs_json, render_items, app_path, absolute_url) {
    callback_1.defer(function () { return _embed_items(docs_json, render_items, app_path, absolute_url); });
}
exports.embed_items = embed_items;
function _embed_items(docs_json, render_items, app_path, absolute_url) {
    if (types_1.isString(docs_json))
        docs_json = JSON.parse(string_1.unescape(docs_json));
    var docs = {};
    for (var docid in docs_json) {
        var doc_json = docs_json[docid];
        docs[docid] = document_1.Document.from_json(doc_json);
    }
    for (var _i = 0, render_items_2 = render_items; _i < render_items_2.length; _i++) {
        var item = render_items_2[_i];
        var elem = _get_element(item);
        var use_for_title = item.use_for_title != null && item.use_for_title;
        // handle server session cases
        if (item.sessionid != null) {
            var websocket_url = _get_ws_url(app_path, absolute_url);
            logging_1.logger.debug("embed: computed ws url: " + websocket_url);
            var promise = void 0;
            if (item.modelid != null)
                promise = add_model_from_session(elem, websocket_url, item.modelid, item.sessionid);
            else
                promise = add_document_from_session(elem, websocket_url, item.sessionid, use_for_title);
            promise.then(function () {
                console.log("Bokeh items were rendered successfully");
            }, function (error) {
                console.log("Error rendering Bokeh items ", error);
            });
            // handle standalone document cases
        }
        else if (item.docid != null) {
            if (item.modelid != null)
                add_model_standalone(item.modelid, elem, docs[item.docid]);
            else
                add_document_standalone(docs[item.docid], elem, use_for_title);
        }
        else
            throw new Error("Error rendering Bokeh items to element " + item.elementid + ": no document ID or session ID specified");
    }
}

//# sourceMappingURL=embed.js.map
