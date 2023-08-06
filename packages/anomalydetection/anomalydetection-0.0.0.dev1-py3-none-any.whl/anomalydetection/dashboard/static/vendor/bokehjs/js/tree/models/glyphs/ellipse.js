"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var p = require("core/properties");
var EllipseView = /** @class */ (function (_super) {
    tslib_1.__extends(EllipseView, _super);
    function EllipseView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    EllipseView.prototype._set_data = function () {
        this.max_w2 = 0;
        if (this.model.properties.width.units == "data")
            this.max_w2 = this.max_width / 2;
        this.max_h2 = 0;
        if (this.model.properties.height.units == "data")
            this.max_h2 = this.max_height / 2;
    };
    EllipseView.prototype._map_data = function () {
        if (this.model.properties.width.units == "data")
            this.sw = this.sdist(this.renderer.xscale, this._x, this._width, 'center');
        else
            this.sw = this._width;
        if (this.model.properties.height.units == "data")
            this.sh = this.sdist(this.renderer.yscale, this._y, this._height, 'center');
        else
            this.sh = this._height;
    };
    EllipseView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, sw = _a.sw, sh = _a.sh;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + sw[i] + sh[i] + this._angle[i]))
                continue;
            ctx.beginPath();
            ctx.ellipse(sx[i], sy[i], sw[i] / 2.0, sh[i] / 2.0, this._angle[i], 0, 2 * Math.PI);
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                ctx.fill();
            }
            if (this.visuals.line.doit) {
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    };
    EllipseView.prototype.draw_legend_for_index = function (ctx, _a, index) {
        var x0 = _a.x0, y0 = _a.y0, x1 = _a.x1, y1 = _a.y1;
        var len = index + 1;
        var sx = new Array(len);
        sx[index] = (x0 + x1) / 2;
        var sy = new Array(len);
        sy[index] = (y0 + y1) / 2;
        var scale = this.sw[index] / this.sh[index];
        var d = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.8;
        var sw = new Array(len);
        var sh = new Array(len);
        if (scale > 1) {
            sw[index] = d;
            sh[index] = d / scale;
        }
        else {
            sw[index] = d * scale;
            sh[index] = d;
        }
        this._render(ctx, [index], { sx: sx, sy: sy, sw: sw, sh: sh }); // XXX
    };
    EllipseView.prototype._bounds = function (_a) {
        var minX = _a.minX, maxX = _a.maxX, minY = _a.minY, maxY = _a.maxY;
        return {
            minX: minX - this.max_w2,
            maxX: maxX + this.max_w2,
            minY: minY - this.max_h2,
            maxY: maxY + this.max_h2,
        };
    };
    return EllipseView;
}(xy_glyph_1.XYGlyphView));
exports.EllipseView = EllipseView;
var Ellipse = /** @class */ (function (_super) {
    tslib_1.__extends(Ellipse, _super);
    function Ellipse(attrs) {
        return _super.call(this, attrs) || this;
    }
    Ellipse.initClass = function () {
        this.prototype.type = 'Ellipse';
        this.prototype.default_view = EllipseView;
        this.mixins(['line', 'fill']);
        this.define({
            angle: [p.AngleSpec, 0.0],
            width: [p.DistanceSpec],
            height: [p.DistanceSpec],
        });
    };
    return Ellipse;
}(xy_glyph_1.XYGlyph));
exports.Ellipse = Ellipse;
Ellipse.initClass();

//# sourceMappingURL=ellipse.js.map
