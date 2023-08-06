import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { PointGeometry, RectGeometry } from "core/geometry";
import { DistanceSpec, AngleSpec } from "core/vectorization";
import { LineMixinVector, FillMixinVector } from "core/property_mixins";
import { Line, Fill } from "core/visuals";
import { Arrayable } from "core/types";
import * as p from "core/properties";
import * as spatial from "core/util/spatial";
import { IBBox } from "core/util/bbox";
import { Context2d } from "core/util/canvas";
import { Selection } from "../selections/selection";
import { Scale } from "../scales/scale";
export interface RectData extends XYGlyphData {
    _angle: Arrayable<number>;
    _width: Arrayable<number>;
    _height: Arrayable<number>;
    sw: Arrayable<number>;
    sx0: Arrayable<number>;
    sh: Arrayable<number>;
    sy1: Arrayable<number>;
    ssemi_diag: Arrayable<number>;
    max_width: number;
    max_height: number;
    max_w2: number;
    max_h2: number;
}
export interface RectView extends RectData {
}
export declare class RectView extends XYGlyphView {
    model: Rect;
    visuals: Rect.Visuals;
    protected _set_data(): void;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], {sx, sy, sx0, sy1, sw, sh, _angle}: RectData): void;
    protected _hit_rect(geometry: RectGeometry): Selection;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _map_dist_corner_for_data_side_length(coord: Arrayable<number>, side_length: Arrayable<number>, scale: Scale): [Arrayable<number>, Arrayable<number>];
    protected _ddist(dim: 0 | 1, spts: Arrayable<number>, spans: Arrayable<number>): Arrayable<number>;
    draw_legend_for_index(ctx: Context2d, bbox: IBBox, index: number): void;
    protected _bounds({minX, maxX, minY, maxY}: spatial.Rect): spatial.Rect;
}
export declare namespace Rect {
    interface Mixins extends LineMixinVector, FillMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        angle: AngleSpec;
        width: DistanceSpec;
        height: DistanceSpec;
        dilate: boolean;
    }
    interface Props extends XYGlyph.Props {
        angle: p.AngleSpec;
        width: p.DistanceSpec;
        height: p.DistanceSpec;
        dilate: p.Property<boolean>;
    }
    interface Visuals extends XYGlyph.Visuals {
        line: Line;
        fill: Fill;
    }
}
export interface Rect extends Rect.Attrs {
}
export declare class Rect extends XYGlyph {
    properties: Rect.Props;
    constructor(attrs?: Partial<Rect.Attrs>);
    static initClass(): void;
}
