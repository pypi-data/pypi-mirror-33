"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_view_1 = require("core/dom_view");
var tool_1 = require("./tool");
var dom_1 = require("core/dom");
var p = require("core/properties");
var ButtonToolButtonView = /** @class */ (function (_super) {
    tslib_1.__extends(ButtonToolButtonView, _super);
    function ButtonToolButtonView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    ButtonToolButtonView.prototype.initialize = function (options) {
        var _this = this;
        _super.prototype.initialize.call(this, options);
        this.connect(this.model.change, function () { return _this.render(); });
        this.el.addEventListener("click", function () { return _this._clicked(); });
        this.render();
    };
    ButtonToolButtonView.prototype.css_classes = function () {
        return _super.prototype.css_classes.call(this).concat("bk-toolbar-button");
    };
    ButtonToolButtonView.prototype.render = function () {
        dom_1.empty(this.el);
        this.el.classList.add(this.model.icon);
        this.el.title = this.model.tooltip;
    };
    return ButtonToolButtonView;
}(dom_view_1.DOMView));
exports.ButtonToolButtonView = ButtonToolButtonView;
var ButtonToolView = /** @class */ (function (_super) {
    tslib_1.__extends(ButtonToolView, _super);
    function ButtonToolView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return ButtonToolView;
}(tool_1.ToolView));
exports.ButtonToolView = ButtonToolView;
var ButtonTool = /** @class */ (function (_super) {
    tslib_1.__extends(ButtonTool, _super);
    function ButtonTool(attrs) {
        return _super.call(this, attrs) || this;
    }
    ButtonTool.initClass = function () {
        this.prototype.type = "ButtonTool";
        this.internal({
            disabled: [p.Boolean, false],
        });
    };
    Object.defineProperty(ButtonTool.prototype, "tooltip", {
        get: function () {
            return this.tool_name;
        },
        enumerable: true,
        configurable: true
    });
    return ButtonTool;
}(tool_1.Tool));
exports.ButtonTool = ButtonTool;
ButtonTool.initClass();

//# sourceMappingURL=button_tool.js.map
