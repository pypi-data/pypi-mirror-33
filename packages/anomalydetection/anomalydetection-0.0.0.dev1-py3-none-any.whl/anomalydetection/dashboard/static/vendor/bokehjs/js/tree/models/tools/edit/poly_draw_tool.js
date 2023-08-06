"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var edit_tool_1 = require("./edit_tool");
var PolyDrawToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PolyDrawToolView, _super);
    function PolyDrawToolView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._drawing = false;
        return _this;
    }
    PolyDrawToolView.prototype._tap = function (ev) {
        if (this._drawing) {
            this._draw(ev, 'add');
            this.model.renderers[0].data_source.properties.data.change.emit();
        }
        else {
            var append = ev.shiftKey;
            this._select_event(ev, append, this.model.renderers);
        }
    };
    PolyDrawToolView.prototype._draw = function (ev, mode) {
        var renderer = this.model.renderers[0];
        var point = this._map_drag(ev.sx, ev.sy, renderer);
        if (point == null) {
            return;
        }
        var x = point[0], y = point[1];
        var ds = renderer.data_source;
        var glyph = renderer.glyph;
        var _a = [glyph.xs.field, glyph.ys.field], xkey = _a[0], ykey = _a[1];
        if (mode == 'new') {
            if (xkey)
                ds.get_array(xkey).push([x, x]);
            if (ykey)
                ds.get_array(ykey).push([y, y]);
            this._pad_empty_columns(ds, [xkey, ykey]);
        }
        else if (mode == 'edit') {
            if (xkey) {
                var xs = ds.data[xkey][ds.data[xkey].length - 1];
                xs[xs.length - 1] = x;
            }
            if (ykey) {
                var ys = ds.data[ykey][ds.data[ykey].length - 1];
                ys[ys.length - 1] = y;
            }
        }
        else if (mode == 'add') {
            if (xkey) {
                var xidx = ds.data[xkey].length - 1;
                var xs = ds.get_array(xkey)[xidx];
                var nx = xs[xs.length - 1];
                xs[xs.length - 1] = x;
                xs.push(nx);
            }
            if (ykey) {
                var yidx = ds.data[ykey].length - 1;
                var ys = ds.get_array(ykey)[yidx];
                var ny = ys[ys.length - 1];
                ys[ys.length - 1] = y;
                ys.push(ny);
            }
        }
        ds.change.emit();
    };
    PolyDrawToolView.prototype._doubletap = function (ev) {
        if (!this.model.active) {
            return;
        }
        if (this._drawing) {
            this._drawing = false;
            this._draw(ev, 'edit');
        }
        else {
            this._drawing = true;
            this._draw(ev, 'new');
        }
        this.model.renderers[0].data_source.properties.data.change.emit();
    };
    PolyDrawToolView.prototype._move = function (ev) {
        if (this._drawing) {
            this._draw(ev, 'edit');
        }
    };
    PolyDrawToolView.prototype._remove = function () {
        var renderer = this.model.renderers[0];
        var ds = renderer.data_source;
        var glyph = renderer.glyph;
        var _a = [glyph.xs.field, glyph.ys.field], xkey = _a[0], ykey = _a[1];
        if (xkey) {
            var xidx = ds.data[xkey].length - 1;
            var xs = ds.get_array(xkey)[xidx];
            xs.splice(xs.length - 1, 1);
        }
        if (ykey) {
            var yidx = ds.data[ykey].length - 1;
            var ys = ds.get_array(ykey)[yidx];
            ys.splice(ys.length - 1, 1);
        }
        ds.change.emit();
        ds.properties.data.change.emit();
    };
    PolyDrawToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
            }
            else if (ev.keyCode == dom_1.Keys.Esc) {
                // Type once selection_manager is typed
                if (this._drawing) {
                    this._remove();
                    this._drawing = false;
                }
                var cds = renderer.data_source;
                cds.selection_manager.clear();
            }
        }
    };
    PolyDrawToolView.prototype._pan_start = function (ev) {
        if (!this.model.drag) {
            return;
        }
        this._select_event(ev, true, this.model.renderers);
        this._basepoint = [ev.sx, ev.sy];
    };
    PolyDrawToolView.prototype._pan = function (ev) {
        if (this._basepoint == null || !this.model.drag) {
            return;
        }
        var _a = this._basepoint, bx = _a[0], by = _a[1];
        // Process polygon/line dragging
        for (var _i = 0, _b = this.model.renderers; _i < _b.length; _i++) {
            var renderer = _b[_i];
            var basepoint = this._map_drag(bx, by, renderer);
            var point = this._map_drag(ev.sx, ev.sy, renderer);
            if (point == null || basepoint == null) {
                continue;
            }
            var ds = renderer.data_source;
            // Type once dataspecs are typed
            var glyph = renderer.glyph;
            var _c = [glyph.xs.field, glyph.ys.field], xkey = _c[0], ykey = _c[1];
            if (!xkey && !ykey) {
                continue;
            }
            var x = point[0], y = point[1];
            var px = basepoint[0], py = basepoint[1];
            var _d = [x - px, y - py], dx = _d[0], dy = _d[1];
            for (var _e = 0, _f = ds.selected.indices; _e < _f.length; _e++) {
                var index = _f[_e];
                var length_1 = void 0, xs = void 0, ys = void 0;
                if (xkey)
                    xs = ds.data[xkey][index];
                if (ykey) {
                    ys = ds.data[ykey][index];
                    length_1 = ys.length;
                }
                else {
                    length_1 = xs.length;
                }
                for (var i = 0; i < length_1; i++) {
                    if (xs) {
                        xs[i] += dx;
                    }
                    if (ys) {
                        ys[i] += dy;
                    }
                }
            }
            ds.change.emit();
        }
        this._basepoint = [ev.sx, ev.sy];
    };
    PolyDrawToolView.prototype._pan_end = function (ev) {
        if (!this.model.drag) {
            return;
        }
        this._pan(ev);
        for (var _i = 0, _a = this.model.renderers; _i < _a.length; _i++) {
            var renderer = _a[_i];
            renderer.data_source.selected.indices = [];
            renderer.data_source.properties.data.change.emit();
        }
        this._basepoint = null;
    };
    PolyDrawToolView.prototype.deactivate = function () {
        if (this._drawing) {
            this._remove();
            this._drawing = false;
        }
    };
    return PolyDrawToolView;
}(edit_tool_1.EditToolView));
exports.PolyDrawToolView = PolyDrawToolView;
var PolyDrawTool = /** @class */ (function (_super) {
    tslib_1.__extends(PolyDrawTool, _super);
    function PolyDrawTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Polygon Draw Tool";
        _this.icon = "bk-tool-icon-poly-draw";
        _this.event_type = ["pan", "tap", "move"];
        _this.default_order = 3;
        return _this;
    }
    PolyDrawTool.initClass = function () {
        this.prototype.type = "PolyDrawTool";
        this.prototype.default_view = PolyDrawToolView;
        this.define({
            drag: [p.Bool, true],
        });
    };
    return PolyDrawTool;
}(edit_tool_1.EditTool));
exports.PolyDrawTool = PolyDrawTool;
PolyDrawTool.initClass();

//# sourceMappingURL=poly_draw_tool.js.map
