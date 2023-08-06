import { Visuals, Line, Fill } from "core/visuals";
import { Context2d } from "core/util/canvas";
import { IBBox } from "core/util/bbox";
export declare function generic_line_legend(visuals: Visuals & {
    line: Line;
}, ctx: Context2d, {x0, x1, y0, y1}: IBBox, index: number): void;
export declare function generic_area_legend(visuals: {
    line: Line;
    fill: Fill;
}, ctx: Context2d, {x0, x1, y0, y1}: IBBox, index: number): void;
