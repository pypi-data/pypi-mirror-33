"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function generic_line_legend(visuals, ctx, _a, index) {
    var x0 = _a.x0, x1 = _a.x1, y0 = _a.y0, y1 = _a.y1;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x0, (y0 + y1) / 2);
    ctx.lineTo(x1, (y0 + y1) / 2);
    if (visuals.line.doit) {
        visuals.line.set_vectorize(ctx, index);
        ctx.stroke();
    }
    ctx.restore();
}
exports.generic_line_legend = generic_line_legend;
function generic_area_legend(visuals, ctx, _a, index) {
    var x0 = _a.x0, x1 = _a.x1, y0 = _a.y0, y1 = _a.y1;
    var w = Math.abs(x1 - x0);
    var dw = w * 0.1;
    var h = Math.abs(y1 - y0);
    var dh = h * 0.1;
    var sx0 = x0 + dw;
    var sx1 = x1 - dw;
    var sy0 = y0 + dh;
    var sy1 = y1 - dh;
    if (visuals.fill.doit) {
        visuals.fill.set_vectorize(ctx, index);
        ctx.fillRect(sx0, sy0, sx1 - sx0, sy1 - sy0);
    }
    if (visuals.line.doit) {
        ctx.beginPath();
        ctx.rect(sx0, sy0, sx1 - sx0, sy1 - sy0);
        visuals.line.set_vectorize(ctx, index);
        ctx.stroke();
    }
}
exports.generic_area_legend = generic_area_legend;

//# sourceMappingURL=utils.js.map
