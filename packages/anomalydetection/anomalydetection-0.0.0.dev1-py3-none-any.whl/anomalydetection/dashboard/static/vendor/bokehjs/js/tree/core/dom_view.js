"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var view_1 = require("./view");
var DOM = require("./dom");
var DOMView = /** @class */ (function (_super) {
    tslib_1.__extends(DOMView, _super);
    function DOMView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DOMView.prototype.initialize = function (options) {
        _super.prototype.initialize.call(this, options);
        this._has_finished = false;
        this.el = this._createElement();
    };
    DOMView.prototype.remove = function () {
        DOM.removeElement(this.el);
        _super.prototype.remove.call(this);
    };
    DOMView.prototype.css_classes = function () {
        return [];
    };
    Object.defineProperty(DOMView.prototype, "cursor", {
        get: function () {
            return null;
        },
        enumerable: true,
        configurable: true
    });
    DOMView.prototype.layout = function () { };
    DOMView.prototype.render = function () { };
    DOMView.prototype.renderTo = function (element, replace) {
        if (replace === void 0) { replace = false; }
        if (!replace)
            element.appendChild(this.el);
        else
            DOM.replaceWith(element, this.el);
        this.layout();
    };
    DOMView.prototype.has_finished = function () {
        return this._has_finished;
    };
    Object.defineProperty(DOMView.prototype, "_root_element", {
        get: function () {
            return DOM.parent(this.el, ".bk-root") || document.body;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(DOMView.prototype, "solver", {
        get: function () {
            return this.is_root ? this._solver : this.parent.solver;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(DOMView.prototype, "is_idle", {
        get: function () {
            return this.has_finished();
        },
        enumerable: true,
        configurable: true
    });
    DOMView.prototype._createElement = function () {
        return DOM.createElement(this.tagName, { id: this.id, class: this.css_classes() });
    };
    return DOMView;
}(view_1.View));
exports.DOMView = DOMView;
DOMView.prototype.tagName = "div";

//# sourceMappingURL=dom_view.js.map
