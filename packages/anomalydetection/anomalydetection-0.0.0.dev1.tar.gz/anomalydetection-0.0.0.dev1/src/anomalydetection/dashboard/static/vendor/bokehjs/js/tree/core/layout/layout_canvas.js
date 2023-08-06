"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var solver_1 = require("./solver");
var has_props_1 = require("../has_props");
var bbox_1 = require("../util/bbox");
var LayoutCanvas = /** @class */ (function (_super) {
    tslib_1.__extends(LayoutCanvas, _super);
    function LayoutCanvas(attrs) {
        return _super.call(this, attrs) || this;
    }
    LayoutCanvas.initClass = function () {
        this.prototype.type = "LayoutCanvas";
    };
    LayoutCanvas.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._top = new solver_1.Variable(this.toString() + ".top");
        this._left = new solver_1.Variable(this.toString() + ".left");
        this._width = new solver_1.Variable(this.toString() + ".width");
        this._height = new solver_1.Variable(this.toString() + ".height");
        this._right = new solver_1.Variable(this.toString() + ".right");
        this._bottom = new solver_1.Variable(this.toString() + ".bottom");
        this._hcenter = new solver_1.Variable(this.toString() + ".hcenter");
        this._vcenter = new solver_1.Variable(this.toString() + ".vcenter");
    };
    LayoutCanvas.prototype.get_editables = function () {
        return [];
    };
    LayoutCanvas.prototype.get_constraints = function () {
        return [
            solver_1.GE(this._top),
            solver_1.GE(this._bottom),
            solver_1.GE(this._left),
            solver_1.GE(this._right),
            solver_1.GE(this._width),
            solver_1.GE(this._height),
            solver_1.EQ(this._left, this._width, [-1, this._right]),
            solver_1.EQ(this._top, this._height, [-1, this._bottom]),
            solver_1.EQ([2, this._hcenter], [-1, this._left], [-1, this._right]),
            solver_1.EQ([2, this._vcenter], [-1, this._top], [-1, this._bottom]),
        ];
    };
    LayoutCanvas.prototype.get_layoutable_children = function () {
        return [];
    };
    Object.defineProperty(LayoutCanvas.prototype, "bbox", {
        get: function () {
            return new bbox_1.BBox({
                x0: this._left.value, y0: this._top.value,
                x1: this._right.value, y1: this._bottom.value,
            });
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(LayoutCanvas.prototype, "layout_bbox", {
        get: function () {
            return {
                top: this._top.value,
                left: this._left.value,
                width: this._width.value,
                height: this._height.value,
                right: this._right.value,
                bottom: this._bottom.value,
                hcenter: this._hcenter.value,
                vcenter: this._vcenter.value,
            };
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(LayoutCanvas.prototype, "xview", {
        get: function () {
            var _this = this;
            return {
                compute: function (x) {
                    return _this._left.value + x;
                },
                v_compute: function (xx) {
                    var _xx = new Float64Array(xx.length);
                    var left = _this._left.value;
                    for (var i = 0; i < xx.length; i++) {
                        _xx[i] = left + xx[i];
                    }
                    return _xx;
                },
            };
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(LayoutCanvas.prototype, "yview", {
        get: function () {
            var _this = this;
            return {
                compute: function (y) {
                    return _this._bottom.value - y;
                },
                v_compute: function (yy) {
                    var _yy = new Float64Array(yy.length);
                    var bottom = _this._bottom.value;
                    for (var i = 0; i < yy.length; i++) {
                        _yy[i] = bottom - yy[i];
                    }
                    return _yy;
                },
            };
        },
        enumerable: true,
        configurable: true
    });
    return LayoutCanvas;
}(has_props_1.HasProps));
exports.LayoutCanvas = LayoutCanvas;
LayoutCanvas.initClass();

//# sourceMappingURL=layout_canvas.js.map
