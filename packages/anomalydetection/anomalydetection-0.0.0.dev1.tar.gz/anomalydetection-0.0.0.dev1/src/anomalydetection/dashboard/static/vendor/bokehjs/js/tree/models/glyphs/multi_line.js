"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var spatial_1 = require("core/util/spatial");
var hittest = require("core/hittest");
var object_1 = require("core/util/object");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
var glyph_1 = require("./glyph");
var utils_1 = require("./utils");
var MultiLineView = /** @class */ (function (_super) {
    tslib_1.__extends(MultiLineView, _super);
    function MultiLineView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    MultiLineView.prototype._index_data = function () {
        var points = [];
        for (var i = 0, end = this._xs.length; i < end; i++) {
            if (this._xs[i] == null || this._xs[i].length === 0)
                continue;
            var _xsi = this._xs[i];
            var xs = [];
            for (var j = 0, n = _xsi.length; j < n; j++) {
                var x = _xsi[j];
                if (!types_1.isStrictNaN(x))
                    xs.push(x);
            }
            var _ysi = this._ys[i];
            var ys = [];
            for (var j = 0, n = _ysi.length; j < n; j++) {
                var y = _ysi[j];
                if (!types_1.isStrictNaN(y))
                    ys.push(y);
            }
            var _a = [array_1.min(xs), array_1.max(xs)], minX = _a[0], maxX = _a[1];
            var _b = [array_1.min(ys), array_1.max(ys)], minY = _b[0], maxY = _b[1];
            points.push({ minX: minX, minY: minY, maxX: maxX, maxY: maxY, i: i });
        }
        return new spatial_1.SpatialIndex(points);
    };
    MultiLineView.prototype._render = function (ctx, indices, _a) {
        var sxs = _a.sxs, sys = _a.sys;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            var _b = [sxs[i], sys[i]], sx = _b[0], sy = _b[1];
            this.visuals.line.set_vectorize(ctx, i);
            for (var j = 0, end = sx.length; j < end; j++) {
                if (j == 0) {
                    ctx.beginPath();
                    ctx.moveTo(sx[j], sy[j]);
                    continue;
                }
                else if (isNaN(sx[j]) || isNaN(sy[j])) {
                    ctx.stroke();
                    ctx.beginPath();
                    continue;
                }
                else
                    ctx.lineTo(sx[j], sy[j]);
            }
            ctx.stroke();
        }
    };
    MultiLineView.prototype._hit_point = function (geometry) {
        var result = hittest.create_empty_hit_test_result();
        var point = { x: geometry.sx, y: geometry.sy };
        var shortest = 9999;
        var hits = {};
        for (var i = 0, end = this.sxs.length; i < end; i++) {
            var threshold = Math.max(2, this.visuals.line.cache_select('line_width', i) / 2);
            var points = null;
            for (var j = 0, endj = this.sxs[i].length - 1; j < endj; j++) {
                var p0 = { x: this.sxs[i][j], y: this.sys[i][j] };
                var p1 = { x: this.sxs[i][j + 1], y: this.sys[i][j + 1] };
                var dist = hittest.dist_to_segment(point, p0, p1);
                if (dist < threshold && dist < shortest) {
                    shortest = dist;
                    points = [j];
                }
            }
            if (points)
                hits[i] = points;
        }
        result.indices = object_1.keys(hits).map(function (x) { return parseInt(x, 10); });
        result.multiline_indices = hits;
        return result;
    };
    MultiLineView.prototype._hit_span = function (geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var result = hittest.create_empty_hit_test_result();
        var val;
        var values;
        if (geometry.direction === 'v') {
            val = this.renderer.yscale.invert(sy);
            values = this._ys;
        }
        else {
            val = this.renderer.xscale.invert(sx);
            values = this._xs;
        }
        var hits = {};
        for (var i = 0, end = values.length; i < end; i++) {
            var points = [];
            for (var j = 0, endj = values[i].length - 1; j < endj; j++) {
                if (values[i][j] <= val && val <= values[i][j + 1])
                    points.push(j);
            }
            if (points.length > 0)
                hits[i] = points;
        }
        result.indices = object_1.keys(hits).map(function (x) { return parseInt(x, 10); });
        result.multiline_indices = hits;
        return result;
    };
    MultiLineView.prototype.get_interpolation_hit = function (i, point_i, geometry) {
        var sx = geometry.sx, sy = geometry.sy;
        var x2 = this._xs[i][point_i];
        var y2 = this._ys[i][point_i];
        var x3 = this._xs[i][point_i + 1];
        var y3 = this._ys[i][point_i + 1];
        var x0, x1;
        var y0, y1;
        if (geometry.type == 'point') {
            ;
            _a = this.renderer.yscale.r_invert(sy - 1, sy + 1), y0 = _a[0], y1 = _a[1];
            _b = this.renderer.xscale.r_invert(sx - 1, sx + 1), x0 = _b[0], x1 = _b[1];
        }
        else {
            if (geometry.direction == 'v') {
                ;
                _c = this.renderer.yscale.r_invert(sy, sy), y0 = _c[0], y1 = _c[1];
                _d = [x2, x3], x0 = _d[0], x1 = _d[1];
            }
            else {
                ;
                _e = this.renderer.xscale.r_invert(sx, sx), x0 = _e[0], x1 = _e[1];
                _f = [y2, y3], y0 = _f[0], y1 = _f[1];
            }
        }
        var _g = hittest.check_2_segments_intersect(x0, y0, x1, y1, x2, y2, x3, y3), x = _g.x, y = _g.y;
        return [x, y]; // XXX: null is not handled at use sites
        var _a, _b, _c, _d, _e, _f;
    };
    MultiLineView.prototype.draw_legend_for_index = function (ctx, bbox, index) {
        utils_1.generic_line_legend(this.visuals, ctx, bbox, index);
    };
    MultiLineView.prototype.scenterx = function () {
        throw new Error("not implemented");
    };
    MultiLineView.prototype.scentery = function () {
        throw new Error("not implemented");
    };
    return MultiLineView;
}(glyph_1.GlyphView));
exports.MultiLineView = MultiLineView;
var MultiLine = /** @class */ (function (_super) {
    tslib_1.__extends(MultiLine, _super);
    function MultiLine(attrs) {
        return _super.call(this, attrs) || this;
    }
    MultiLine.initClass = function () {
        this.prototype.type = 'MultiLine';
        this.prototype.default_view = MultiLineView;
        this.coords([['xs', 'ys']]);
        this.mixins(['line']);
    };
    return MultiLine;
}(glyph_1.Glyph));
exports.MultiLine = MultiLine;
MultiLine.initClass();

//# sourceMappingURL=multi_line.js.map
