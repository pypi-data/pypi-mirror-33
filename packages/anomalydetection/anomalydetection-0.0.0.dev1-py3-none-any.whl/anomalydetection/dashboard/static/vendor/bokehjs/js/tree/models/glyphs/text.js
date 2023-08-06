"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var xy_glyph_1 = require("./xy_glyph");
var p = require("core/properties");
var text_1 = require("core/util/text");
var TextView = /** @class */ (function (_super) {
    tslib_1.__extends(TextView, _super);
    function TextView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    TextView.prototype._render = function (ctx, indices, _a) {
        var sx = _a.sx, sy = _a.sy, _x_offset = _a._x_offset, _y_offset = _a._y_offset, _angle = _a._angle, _text = _a._text;
        for (var _i = 0, indices_1 = indices; _i < indices_1.length; _i++) {
            var i = indices_1[_i];
            if (isNaN(sx[i] + sy[i] + _x_offset[i] + _y_offset[i] + _angle[i]) || _text[i] == null)
                continue;
            if (this.visuals.text.doit) {
                var text = "" + _text[i];
                ctx.save();
                ctx.translate(sx[i] + _x_offset[i], sy[i] + _y_offset[i]);
                ctx.rotate(_angle[i]);
                this.visuals.text.set_vectorize(ctx, i);
                if (text.indexOf("\n") == -1)
                    ctx.fillText(text, 0, 0);
                else {
                    var lines = text.split("\n");
                    var font = this.visuals.text.cache_select("font", i);
                    var height = text_1.get_text_height(font).height;
                    var line_height = this.visuals.text.text_line_height.value() * height;
                    var block_height = line_height * lines.length;
                    var baseline = this.visuals.text.cache_select("text_baseline", i);
                    var y = void 0;
                    switch (baseline) {
                        case "top": {
                            y = 0;
                            break;
                        }
                        case "middle": {
                            y = (-block_height / 2) + (line_height / 2);
                            break;
                        }
                        case "bottom": {
                            y = -block_height + line_height;
                            break;
                        }
                        default: {
                            y = 0;
                            console.warn("'" + baseline + "' baseline not supported with multi line text");
                        }
                    }
                    for (var _b = 0, lines_1 = lines; _b < lines_1.length; _b++) {
                        var line = lines_1[_b];
                        ctx.fillText(line, 0, y);
                        y += line_height;
                    }
                }
                ctx.restore();
            }
        }
    };
    return TextView;
}(xy_glyph_1.XYGlyphView));
exports.TextView = TextView;
var Text = /** @class */ (function (_super) {
    tslib_1.__extends(Text, _super);
    function Text(attrs) {
        return _super.call(this, attrs) || this;
    }
    Text.initClass = function () {
        this.prototype.type = 'Text';
        this.prototype.default_view = TextView;
        this.mixins(['text']);
        this.define({
            text: [p.StringSpec, { field: "text" }],
            angle: [p.AngleSpec, 0],
            x_offset: [p.NumberSpec, 0],
            y_offset: [p.NumberSpec, 0],
        });
    };
    return Text;
}(xy_glyph_1.XYGlyph));
exports.Text = Text;
Text.initClass();

//# sourceMappingURL=text.js.map
