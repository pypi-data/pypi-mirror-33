"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var inspect_tool_1 = require("./inspect_tool");
var tooltip_1 = require("../../annotations/tooltip");
var glyph_renderer_1 = require("../../renderers/glyph_renderer");
var graph_renderer_1 = require("../../renderers/graph_renderer");
var util_1 = require("../util");
var hittest = require("core/hittest");
var templating_1 = require("core/util/templating");
var dom_1 = require("core/dom");
var p = require("core/properties");
var color_1 = require("core/util/color");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
var build_views_1 = require("core/build_views");
function _nearest_line_hit(i, geometry, sx, sy, dx, dy) {
    var d1 = { x: dx[i], y: dy[i] };
    var d2 = { x: dx[i + 1], y: dy[i + 1] };
    var dist1;
    var dist2;
    if (geometry.type == "span") {
        if (geometry.direction == "h") {
            dist1 = Math.abs(d1.x - sx);
            dist2 = Math.abs(d2.x - sx);
        }
        else {
            dist1 = Math.abs(d1.y - sy);
            dist2 = Math.abs(d2.y - sy);
        }
    }
    else {
        var s = { x: sx, y: sy };
        dist1 = hittest.dist_2_pts(d1, s);
        dist2 = hittest.dist_2_pts(d2, s);
    }
    if (dist1 < dist2)
        return [[d1.x, d1.y], i];
    else
        return [[d2.x, d2.y], i + 1];
}
exports._nearest_line_hit = _nearest_line_hit;
function _line_hit(xs, ys, ind) {
    return [[xs[ind], ys[ind]], ind];
}
exports._line_hit = _line_hit;
var HoverToolView = /** @class */ (function (_super) {
    tslib_1.__extends(HoverToolView, _super);
    function HoverToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    HoverToolView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this.ttviews = {};
    };
    HoverToolView.prototype.remove = function () {
        build_views_1.remove_views(this.ttviews);
        _super.prototype.remove.call(this);
    };
    HoverToolView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
            var r = _a[_i];
            // XXX: no typings
            if (r instanceof glyph_renderer_1.GlyphRenderer) {
                this.connect(r.data_source.inspect, this._update);
            }
            else if (r instanceof graph_renderer_1.GraphRenderer) {
                this.connect(r.node_renderer.data_source.inspect, this._update);
                this.connect(r.edge_renderer.data_source.inspect, this._update);
            }
        }
        // TODO: this.connect(this.plot_model.plot.properties.renderers.change, () => this._computed_renderers = this._ttmodels = null)
        this.connect(this.model.properties.renderers.change, function () { return _this._computed_renderers = _this._ttmodels = null; });
        this.connect(this.model.properties.names.change, function () { return _this._computed_renderers = _this._ttmodels = null; });
        this.connect(this.model.properties.tooltips.change, function () { return _this._ttmodels = null; });
    };
    HoverToolView.prototype._compute_ttmodels = function () {
        var ttmodels = {};
        var tooltips = this.model.tooltips;
        if (tooltips != null) {
            for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
                var r = _a[_i];
                if (r instanceof glyph_renderer_1.GlyphRenderer) {
                    var tooltip = new tooltip_1.Tooltip({
                        custom: types_1.isString(tooltips) || types_1.isFunction(tooltips),
                        attachment: this.model.attachment,
                        show_arrow: this.model.show_arrow,
                    });
                    ttmodels[r.id] = tooltip;
                }
                else if (r instanceof graph_renderer_1.GraphRenderer) {
                    var tooltip = new tooltip_1.Tooltip({
                        custom: types_1.isString(tooltips) || types_1.isFunction(tooltips),
                        attachment: this.model.attachment,
                        show_arrow: this.model.show_arrow,
                    });
                    /// XXX: no typings
                    ttmodels[r.node_renderer.id] = tooltip;
                    ttmodels[r.edge_renderer.id] = tooltip;
                }
            }
        }
        build_views_1.build_views(this.ttviews, object_1.values(ttmodels), { parent: this, plot_view: this.plot_view });
        return ttmodels;
    };
    Object.defineProperty(HoverToolView.prototype, "computed_renderers", {
        get: function () {
            if (this._computed_renderers == null) {
                var renderers = this.model.renderers;
                var all_renderers = this.plot_model.plot.renderers;
                var names = this.model.names;
                this._computed_renderers = util_1.compute_renderers(renderers, all_renderers, names);
            }
            return this._computed_renderers;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(HoverToolView.prototype, "ttmodels", {
        get: function () {
            if (this._ttmodels == null)
                this._ttmodels = this._compute_ttmodels();
            return this._ttmodels;
        },
        enumerable: true,
        configurable: true
    });
    HoverToolView.prototype._clear = function () {
        this._inspect(Infinity, Infinity);
        for (var rid in this.ttmodels) {
            var tt = this.ttmodels[rid];
            tt.clear();
        }
    };
    HoverToolView.prototype._move = function (ev) {
        if (!this.model.active)
            return;
        var sx = ev.sx, sy = ev.sy;
        if (!this.plot_model.frame.bbox.contains(sx, sy))
            this._clear();
        else
            this._inspect(sx, sy);
    };
    HoverToolView.prototype._move_exit = function () {
        this._clear();
    };
    HoverToolView.prototype._inspect = function (sx, sy) {
        var geometry;
        if (this.model.mode == 'mouse')
            geometry = { type: 'point', sx: sx, sy: sy };
        else {
            var direction = this.model.mode == 'vline' ? 'h' : 'v';
            geometry = { type: 'span', direction: direction, sx: sx, sy: sy };
        }
        for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
            var r = _a[_i];
            var sm = r.get_selection_manager();
            sm.inspect(this.plot_view.renderer_views[r.id], geometry);
        }
        if (this.model.callback != null)
            this._emit_callback(geometry);
    };
    HoverToolView.prototype._update = function (_a) {
        var renderer_view = _a[0], geometry = _a[1].geometry;
        if (!this.model.active)
            return;
        var tooltip = this.ttmodels[renderer_view.model.id];
        if (tooltip == null)
            return;
        tooltip.clear();
        var indices = renderer_view.model.get_selection_manager().inspectors[renderer_view.model.id];
        if (renderer_view.model instanceof glyph_renderer_1.GlyphRenderer)
            indices = renderer_view.model.view.convert_selection_to_subset(indices);
        var ds = renderer_view.model.get_selection_manager().source;
        if (indices.is_empty())
            return;
        var frame = this.plot_model.frame;
        var sx = geometry.sx, sy = geometry.sy;
        var xscale = frame.xscales[renderer_view.model.x_range_name]; // XXX: bad class structure
        var yscale = frame.yscales[renderer_view.model.y_range_name];
        var x = xscale.invert(sx);
        var y = yscale.invert(sy);
        var glyph = renderer_view.glyph; // XXX
        for (var _i = 0, _b = indices.line_indices; _i < _b.length; _i++) {
            var i = _b[_i];
            var data_x = glyph._x[i + 1];
            var data_y = glyph._y[i + 1];
            var ii = i;
            var rx = void 0;
            var ry = void 0;
            switch (this.model.line_policy) {
                case "interp": { // and renderer.get_interpolation_hit?
                    _c = glyph.get_interpolation_hit(i, geometry), data_x = _c[0], data_y = _c[1];
                    rx = xscale.compute(data_x);
                    ry = yscale.compute(data_y);
                    break;
                }
                case "prev": {
                    _d = _line_hit(glyph.sx, glyph.sy, i), _e = _d[0], rx = _e[0], ry = _e[1], ii = _d[1];
                    break;
                }
                case "next": {
                    _f = _line_hit(glyph.sx, glyph.sy, i + 1), _g = _f[0], rx = _g[0], ry = _g[1], ii = _f[1];
                    break;
                }
                case "nearest": {
                    _h = _nearest_line_hit(i, geometry, sx, sy, glyph.sx, glyph.sy), _j = _h[0], rx = _j[0], ry = _j[1], ii = _h[1];
                    data_x = glyph._x[ii];
                    data_y = glyph._y[ii];
                    break;
                }
                default: {
                    _k = [sx, sy], rx = _k[0], ry = _k[1];
                }
            }
            var vars = { index: ii, x: x, y: y, sx: sx, sy: sy, data_x: data_x, data_y: data_y, rx: rx, ry: ry, indices: indices.line_indices };
            tooltip.add(rx, ry, this._render_tooltips(ds, ii, vars));
        }
        for (var _l = 0, _m = indices.image_indices; _l < _m.length; _l++) {
            var struct = _m[_l];
            var vars = { index: struct['index'], x: x, y: y, sx: sx, sy: sy };
            var rendered = this._render_tooltips(ds, struct, vars);
            tooltip.add(sx, sy, rendered);
        }
        for (var _o = 0, _p = indices.indices; _o < _p.length; _o++) {
            var i = _p[_o];
            // multiglyphs set additional indices, e.g. multiline_indices for different tooltips
            if (!object_1.isEmpty(indices.multiline_indices)) {
                for (var _q = 0, _r = indices.multiline_indices[i.toString()]; _q < _r.length; _q++) {
                    var j = _r[_q];
                    var data_x = glyph._xs[i][j];
                    var data_y = glyph._ys[i][j];
                    var jj = j;
                    var rx = void 0;
                    var ry = void 0;
                    switch (this.model.line_policy) {
                        case "interp": { // and renderer.get_interpolation_hit?
                            _s = glyph.get_interpolation_hit(i, j, geometry), data_x = _s[0], data_y = _s[1];
                            rx = xscale.compute(data_x);
                            ry = yscale.compute(data_y);
                            break;
                        }
                        case "prev": {
                            _t = _line_hit(glyph.sxs[i], glyph.sys[i], j), _u = _t[0], rx = _u[0], ry = _u[1], jj = _t[1];
                            break;
                        }
                        case "next": {
                            _v = _line_hit(glyph.sxs[i], glyph.sys[i], j + 1), _w = _v[0], rx = _w[0], ry = _w[1], jj = _v[1];
                            break;
                        }
                        case "nearest": {
                            _z = _nearest_line_hit(j, geometry, sx, sy, glyph.sxs[i], glyph.sys[i]), _0 = _z[0], rx = _0[0], ry = _0[1], jj = _z[1];
                            data_x = glyph._xs[i][jj];
                            data_y = glyph._ys[i][jj];
                            break;
                        }
                        default:
                            throw new Error("should't have happened");
                    }
                    var index = void 0;
                    if (renderer_view.model instanceof glyph_renderer_1.GlyphRenderer)
                        index = renderer_view.model.view.convert_indices_from_subset([i])[0];
                    else
                        index = i; // XXX: ???
                    var vars = { index: index, segment_index: jj, x: x, y: y, sx: sx, sy: sy, data_x: data_x, data_y: data_y, indices: indices.multiline_indices };
                    tooltip.add(rx, ry, this._render_tooltips(ds, index, vars));
                }
            }
            else {
                // handle non-multiglyphs
                var data_x = glyph._x != null ? glyph._x[i] : undefined;
                var data_y = glyph._y != null ? glyph._y[i] : undefined;
                var rx = void 0;
                var ry = void 0;
                if (this.model.point_policy == 'snap_to_data') { // and renderer.glyph.sx? and renderer.glyph.sy?
                    // Pass in our screen position so we can determine which patch we're
                    // over if there are discontinuous patches.
                    var pt = glyph.get_anchor_point(this.model.anchor, i, [sx, sy]);
                    if (pt == null)
                        pt = glyph.get_anchor_point("center", i, [sx, sy]);
                    rx = pt.x;
                    ry = pt.y;
                }
                else
                    _1 = [sx, sy], rx = _1[0], ry = _1[1];
                var index = void 0;
                if (renderer_view.model instanceof glyph_renderer_1.GlyphRenderer)
                    index = renderer_view.model.view.convert_indices_from_subset([i])[0];
                else
                    index = i;
                var vars = { index: index, x: x, y: y, sx: sx, sy: sy, data_x: data_x, data_y: data_y, indices: indices.indices };
                tooltip.add(rx, ry, this._render_tooltips(ds, index, vars));
            }
        }
        var _c, _d, _e, _f, _g, _h, _j, _k, _s, _t, _u, _v, _w, _z, _0, _1;
    };
    HoverToolView.prototype._emit_callback = function (geometry) {
        for (var _i = 0, _a = this.computed_renderers; _i < _a.length; _i++) {
            var r = _a[_i];
            var index = r.data_source.inspected;
            var frame = this.plot_model.frame;
            var xscale = frame.xscales[r.x_range_name];
            var yscale = frame.yscales[r.y_range_name];
            var x = xscale.invert(geometry.sx);
            var y = yscale.invert(geometry.sy);
            var g = object_1.extend({ x: x, y: y }, geometry);
            var callback = this.model.callback;
            var _b = [callback, { index: index, geometry: g, renderer: r }], obj = _b[0], data = _b[1];
            if (types_1.isFunction(callback))
                callback(obj, data);
            else
                callback.execute(obj, data);
        }
    };
    HoverToolView.prototype._render_tooltips = function (ds, i, vars) {
        var tooltips = this.model.tooltips;
        if (types_1.isString(tooltips)) {
            var el = dom_1.div();
            el.innerHTML = templating_1.replace_placeholders(tooltips, ds, i, this.model.formatters, vars);
            return el;
        }
        else if (types_1.isFunction(tooltips)) {
            return tooltips(ds, vars);
        }
        else {
            var rows = dom_1.div({ style: { display: "table", borderSpacing: "2px" } });
            for (var _i = 0, tooltips_1 = tooltips; _i < tooltips_1.length; _i++) {
                var _a = tooltips_1[_i], label = _a[0], value = _a[1];
                var row = dom_1.div({ style: { display: "table-row" } });
                rows.appendChild(row);
                var cell = void 0;
                cell = dom_1.div({ style: { display: "table-cell" }, class: 'bk-tooltip-row-label' }, label + ": ");
                row.appendChild(cell);
                cell = dom_1.div({ style: { display: "table-cell" }, class: 'bk-tooltip-row-value' });
                row.appendChild(cell);
                if (value.indexOf("$color") >= 0) {
                    var _b = value.match(/\$color(\[.*\])?:(\w*)/), _c = _b[1], opts = _c === void 0 ? "" : _c, colname = _b[2]; // XXX!
                    var column = ds.get_column(colname); // XXX: change to columnar ds
                    if (column == null) {
                        var el_1 = dom_1.span({}, colname + " unknown");
                        cell.appendChild(el_1);
                        continue;
                    }
                    var hex = opts.indexOf("hex") >= 0;
                    var swatch = opts.indexOf("swatch") >= 0;
                    var color = types_1.isNumber(i) ? column[i] : null;
                    if (color == null) {
                        var el_2 = dom_1.span({}, "(null)");
                        cell.appendChild(el_2);
                        continue;
                    }
                    if (hex)
                        color = color_1.color2hex(color);
                    var el = dom_1.span({}, color);
                    cell.appendChild(el);
                    if (swatch) {
                        el = dom_1.span({ class: 'bk-tooltip-color-block', style: { backgroundColor: color } }, " ");
                        cell.appendChild(el);
                    }
                }
                else {
                    var el = dom_1.span();
                    el.innerHTML = templating_1.replace_placeholders(value.replace("$~", "$data_"), ds, i, this.model.formatters, vars);
                    cell.appendChild(el);
                }
            }
            return rows;
        }
    };
    return HoverToolView;
}(inspect_tool_1.InspectToolView));
exports.HoverToolView = HoverToolView;
var HoverTool = /** @class */ (function (_super) {
    tslib_1.__extends(HoverTool, _super);
    function HoverTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Hover";
        _this.icon = "bk-tool-icon-hover";
        return _this;
    }
    HoverTool.initClass = function () {
        this.prototype.type = "HoverTool";
        this.prototype.default_view = HoverToolView;
        this.define({
            tooltips: [p.Any, [
                    ["index", "$index"],
                    ["data (x, y)", "($x, $y)"],
                    ["screen (x, y)", "($sx, $sy)"],
                ]],
            formatters: [p.Any, {}],
            renderers: [p.Any, 'auto'],
            names: [p.Array, []],
            mode: [p.String, 'mouse'],
            point_policy: [p.String, 'snap_to_data'],
            line_policy: [p.String, 'nearest'],
            show_arrow: [p.Boolean, true],
            anchor: [p.String, 'center'],
            attachment: [p.String, 'horizontal'],
            callback: [p.Any],
        });
    };
    return HoverTool;
}(inspect_tool_1.InspectTool));
exports.HoverTool = HoverTool;
HoverTool.initClass();

//# sourceMappingURL=hover_tool.js.map
