import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { DistanceSpec, AngleSpec } from "core/vectorization";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import { Rect } from "core/util/spatial";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
export interface OvalData extends XYGlyphData {
    _angle: Arrayable<number>;
    _width: Arrayable<number>;
    _height: Arrayable<number>;
    sw: Arrayable<number>;
    sh: Arrayable<number>;
    max_width: number;
    max_height: number;
    max_w2: number;
    max_h2: number;
}
export interface OvalView extends OvalData {
}
export declare class OvalView extends XYGlyphView {
    model: Oval;
    visuals: Oval.Visuals;
    _set_data(): void;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], {sx, sy, sw, sh, _angle}: OvalData): void;
    draw_legend_for_index(ctx: Context2d, {x0, y0, x1, y1}: IBBox, index: number): void;
    protected _bounds({minX, maxX, minY, maxY}: Rect): Rect;
}
export declare namespace Oval {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        angle: AngleSpec;
        width: DistanceSpec;
        height: DistanceSpec;
    }
    interface Props extends XYGlyph.Props {
        angle: p.AngleSpec;
        width: p.DistanceSpec;
        height: p.DistanceSpec;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface Oval extends Oval.Attrs {
}
export declare class Oval extends XYGlyph {
    properties: Oval.Props;
    constructor(attrs?: Partial<Oval.Attrs>);
    static initClass(): void;
}
