"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var range_1 = require("./range");
var p = require("core/properties");
var Range1d = /** @class */ (function (_super) {
    tslib_1.__extends(Range1d, _super);
    function Range1d(attrs) {
        return _super.call(this, attrs) || this;
    }
    Range1d.initClass = function () {
        this.prototype.type = "Range1d";
        this.define({
            start: [p.Number, 0],
            end: [p.Number, 1],
        });
    };
    Range1d.prototype._set_auto_bounds = function () {
        if (this.bounds == 'auto') {
            var min = Math.min(this._initial_start, this._initial_end);
            var max = Math.max(this._initial_start, this._initial_end);
            this.setv({ bounds: [min, max] }, { silent: true });
        }
    };
    Range1d.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this._initial_start = this.start;
        this._initial_end = this.end;
        this._set_auto_bounds();
    };
    Object.defineProperty(Range1d.prototype, "min", {
        get: function () {
            return Math.min(this.start, this.end);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Range1d.prototype, "max", {
        get: function () {
            return Math.max(this.start, this.end);
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Range1d.prototype, "is_reversed", {
        get: function () {
            return this.start > this.end;
        },
        enumerable: true,
        configurable: true
    });
    Range1d.prototype.reset = function () {
        this._set_auto_bounds();
        if (this.start != this._initial_start || this.end != this._initial_end)
            this.setv({ start: this._initial_start, end: this._initial_end });
        else
            this.change.emit();
    };
    return Range1d;
}(range_1.Range));
exports.Range1d = Range1d;
Range1d.initClass();

//# sourceMappingURL=range1d.js.map
