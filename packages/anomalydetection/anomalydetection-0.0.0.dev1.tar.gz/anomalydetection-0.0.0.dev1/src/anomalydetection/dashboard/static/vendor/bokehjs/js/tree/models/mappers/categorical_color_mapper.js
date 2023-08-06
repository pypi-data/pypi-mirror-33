"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var color_mapper_1 = require("./color_mapper");
var p = require("core/properties");
var array_1 = require("core/util/array");
var types_1 = require("core/util/types");
function _equals(a, b) {
    if (a.length != b.length)
        return false;
    for (var i = 0, end = a.length; i < end; i++) {
        if (a[i] !== b[i])
            return false;
    }
    return true;
}
var CategoricalColorMapper = /** @class */ (function (_super) {
    tslib_1.__extends(CategoricalColorMapper, _super);
    function CategoricalColorMapper(attrs) {
        return _super.call(this, attrs) || this;
    }
    CategoricalColorMapper.initClass = function () {
        this.prototype.type = "CategoricalColorMapper";
        this.define({
            factors: [p.Array],
            start: [p.Number, 0],
            end: [p.Number],
        });
    };
    CategoricalColorMapper.prototype._v_compute = function (data, values, palette, _a) {
        var nan_color = _a.nan_color;
        var _loop_1 = function (i, end) {
            var d = data[i];
            var key = void 0;
            if (types_1.isString(d))
                key = this_1.factors.indexOf(d);
            else {
                if (this_1.start != null) {
                    if (this_1.end != null)
                        d = d.slice(this_1.start, this_1.end);
                    else
                        d = d.slice(this_1.start);
                }
                else if (this_1.end != null)
                    d = d.slice(0, this_1.end);
                if (d.length == 1)
                    key = this_1.factors.indexOf(d[0]);
                else
                    key = array_1.findIndex(this_1.factors, function (x) { return _equals(x, d); });
            }
            var color = void 0;
            if (key < 0 || key >= palette.length)
                color = nan_color;
            else
                color = palette[key];
            values[i] = color;
        };
        var this_1 = this;
        for (var i = 0, end = data.length; i < end; i++) {
            _loop_1(i, end);
        }
    };
    return CategoricalColorMapper;
}(color_mapper_1.ColorMapper));
exports.CategoricalColorMapper = CategoricalColorMapper;
CategoricalColorMapper.initClass();

//# sourceMappingURL=categorical_color_mapper.js.map
