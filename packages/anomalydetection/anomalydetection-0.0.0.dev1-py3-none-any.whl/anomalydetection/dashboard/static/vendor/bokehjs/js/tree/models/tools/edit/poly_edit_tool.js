"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var dom_1 = require("core/dom");
var p = require("core/properties");
var edit_tool_1 = require("./edit_tool");
var PolyEditToolView = /** @class */ (function (_super) {
    tslib_1.__extends(PolyEditToolView, _super);
    function PolyEditToolView() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this._drawing = false;
        return _this;
    }
    PolyEditToolView.prototype._doubletap = function (ev) {
        if (!this.model.active) {
            return;
        }
        var point = this._map_drag(ev.sx, ev.sy, this.model.vertex_renderer);
        if (point == null) {
            return;
        }
        var x = point[0], y = point[1];
        // Perform hit testing
        var renderers = this._select_event(ev, false, this.model.renderers);
        var vertex_selected = this._select_event(ev, false, [this.model.vertex_renderer]);
        var point_ds = this.model.vertex_renderer.data_source;
        // Type once dataspecs are typed
        var point_glyph = this.model.vertex_renderer.glyph;
        var _a = [point_glyph.x.field, point_glyph.y.field], pxkey = _a[0], pykey = _a[1];
        if (vertex_selected.length && this._selected_renderer != null) {
            // Insert a new point after the selected vertex and enter draw mode
            var index_1 = point_ds.selected.indices[0];
            if (this._drawing) {
                point_ds.selected.indices = [];
                if (pxkey)
                    point_ds.data[pxkey][index_1] = x;
                if (pykey)
                    point_ds.data[pykey][index_1] = y;
                this._drawing = false;
                this._selected_renderer.data_source.properties.data.change.emit();
            }
            else {
                point_ds.selected.indices = [index_1 + 1];
                if (pxkey)
                    point_ds.get_array(pxkey).splice(index_1 + 1, 0, x);
                if (pykey)
                    point_ds.get_array(pykey).splice(index_1 + 1, 0, y);
                this._drawing = true;
            }
            point_ds.change.emit();
            this._selected_renderer.data_source.change.emit();
            return;
        }
        else if (!renderers.length) {
            // If we did not hit an existing line, clear node CDS
            if (pxkey)
                point_ds.data[pxkey] = [];
            if (pykey)
                point_ds.data[pykey] = [];
            this._selected_renderer = null;
            this._drawing = false;
            point_ds.change.emit();
            return;
        }
        // Otherwise copy selected line array to vertex renderer CDS
        // (Note: can only edit one at a time)
        var renderer = renderers[0];
        // Type once dataspecs are typed
        var glyph = renderer.glyph;
        var ds = renderer.data_source;
        var index = ds.selected.indices[0];
        var _b = [glyph.xs.field, glyph.ys.field], xkey = _b[0], ykey = _b[1];
        if (xkey) {
            var xs = ds.data[xkey][index];
            if (pxkey)
                point_ds.data[pxkey] = xs;
        }
        else
            point_glyph.x = { value: glyph.xs.value };
        if (ykey) {
            var ys = ds.data[ykey][index];
            if (pykey)
                point_ds.data[pykey] = ys;
        }
        else
            point_glyph.y = { value: glyph.ys.value };
        point_ds.selected.indices = [];
        this._selected_renderer = renderer;
        point_ds.change.emit();
        point_ds.properties.data.change.emit();
    };
    PolyEditToolView.prototype._move = function (ev) {
        if (this._drawing && this._selected_renderer != null) {
            var renderer = this.model.vertex_renderer;
            var point = this._map_drag(ev.sx, ev.sy, renderer);
            if (point == null) {
                return;
            }
            var x = point[0], y = point[1];
            var ds = renderer.data_source;
            var glyph = renderer.glyph;
            var _a = [glyph.x.field, glyph.y.field], xkey = _a[0], ykey = _a[1];
            var index = ds.selected.indices[0];
            if (xkey)
                ds.data[xkey][index] = x;
            if (ykey)
                ds.data[ykey][index] = y;
            ds.change.emit();
            this._selected_renderer.data_source.change.emit();
        }
    };
    PolyEditToolView.prototype._tap = function (ev) {
        var renderer = this.model.vertex_renderer;
        var point = this._map_drag(ev.sx, ev.sy, renderer);
        if (point == null) {
            return;
        }
        else if (this._drawing && this._selected_renderer) {
            var x = point[0], y = point[1];
            var ds = renderer.data_source;
            // Type once dataspecs are typed
            var glyph = renderer.glyph;
            var _a = [glyph.x.field, glyph.y.field], xkey = _a[0], ykey = _a[1];
            var index = ds.selected.indices[0];
            ds.selected.indices = [index + 1];
            if (xkey) {
                var xs = ds.get_array(xkey);
                var nx = xs[index];
                xs[index] = x;
                xs.splice(index + 1, 0, nx);
            }
            if (ykey) {
                var ys = ds.get_array(ykey);
                var ny = ys[index];
                ys[index] = y;
                ys.splice(index + 1, 0, ny);
            }
            ds.change.emit();
            var selected_ds = this._selected_renderer.data_source;
            selected_ds.change.emit();
            selected_ds.properties.data.change.emit();
            return;
        }
        var append = ev.shiftKey;
        this._select_event(ev, append, [renderer]);
        this._select_event(ev, append, this.model.renderers);
    };
    PolyEditToolView.prototype._remove_vertex = function (emit) {
        if (emit === void 0) { emit = true; }
        if (!this._drawing || !this._selected_renderer) {
            return;
        }
        var renderer = this.model.vertex_renderer;
        var ds = renderer.data_source;
        // Type once dataspecs are typed
        var glyph = renderer.glyph;
        var index = ds.selected.indices[0];
        var _a = [glyph.x.field, glyph.y.field], xkey = _a[0], ykey = _a[1];
        if (xkey)
            ds.get_array(xkey).splice(index, 1);
        if (ykey)
            ds.get_array(ykey).splice(index, 1);
        if (emit) {
            ds.change.emit();
            ds.properties.data.change.emit();
        }
    };
    PolyEditToolView.prototype._pan_start = function (ev) {
        this._select_event(ev, true, [this.model.vertex_renderer]);
        this._basepoint = [ev.sx, ev.sy];
    };
    PolyEditToolView.prototype._pan = function (ev) {
        if (this._basepoint == null) {
            return;
        }
        this._drag_points(ev, [this.model.vertex_renderer]);
        if (this._selected_renderer) {
            this._selected_renderer.data_source.change.emit();
        }
    };
    PolyEditToolView.prototype._pan_end = function (_e) {
        this.model.vertex_renderer.data_source.selected.indices = [];
        if (this._selected_renderer) {
            this._selected_renderer.data_source.properties.data.change.emit();
        }
        this._basepoint = null;
    };
    PolyEditToolView.prototype._keyup = function (ev) {
        if (!this.model.active || !this._mouse_in_frame) {
            return;
        }
        var renderers;
        if (this._selected_renderer) {
            renderers = [this.model.vertex_renderer];
        }
        else {
            renderers = this.model.renderers;
        }
        for (var _i = 0, renderers_1 = renderers; _i < renderers_1.length; _i++) {
            var renderer = renderers_1[_i];
            if (ev.keyCode === dom_1.Keys.Backspace) {
                this._delete_selected(renderer);
            }
            else if (ev.keyCode == dom_1.Keys.Esc) {
                // Type once selection_manager is typed
                if (this._drawing) {
                    this._remove_vertex();
                    this._drawing = false;
                }
                var cds = renderer.data_source;
                cds.selection_manager.clear();
            }
        }
    };
    PolyEditToolView.prototype.deactivate = function () {
        if (!this._selected_renderer) {
            return;
        }
        else if (this._drawing) {
            this._remove_vertex(false);
            this._drawing = false;
        }
        var renderer = this.model.vertex_renderer;
        // Type once selection manager and dataspecs are typed
        var ds = renderer.data_source;
        var glyph = renderer.glyph;
        var _a = [glyph.x.field, glyph.y.field], xkey = _a[0], ykey = _a[1];
        if (xkey)
            ds.data[xkey] = [];
        if (ykey)
            ds.data[ykey] = [];
        ds.selection_manager.clear();
        ds.change.emit();
        this._selected_renderer.data_source.change.emit();
        ds.properties.data.change.emit();
        this._selected_renderer.data_source.properties.data.change.emit();
        this._selected_renderer = null;
    };
    return PolyEditToolView;
}(edit_tool_1.EditToolView));
exports.PolyEditToolView = PolyEditToolView;
var PolyEditTool = /** @class */ (function (_super) {
    tslib_1.__extends(PolyEditTool, _super);
    function PolyEditTool(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.tool_name = "Poly Edit Tool";
        _this.icon = "bk-tool-icon-poly-edit";
        _this.event_type = ["tap", "pan", "move"];
        _this.default_order = 4;
        return _this;
    }
    PolyEditTool.initClass = function () {
        this.prototype.type = "PolyEditTool";
        this.prototype.default_view = PolyEditToolView;
        this.define({
            vertex_renderer: [p.Instance],
        });
    };
    return PolyEditTool;
}(edit_tool_1.EditTool));
exports.PolyEditTool = PolyEditTool;
PolyEditTool.initClass();

//# sourceMappingURL=poly_edit_tool.js.map
