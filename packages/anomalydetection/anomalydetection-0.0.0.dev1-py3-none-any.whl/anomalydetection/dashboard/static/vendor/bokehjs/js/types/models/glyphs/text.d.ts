import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { NumberSpec, StringSpec, AngleSpec } from "core/vectorization";
import { TextMixinVector } from "core/property_mixins";
import { Arrayable } from "core/types";
import * as visuals from "core/visuals";
import { Context2d } from "core/util/canvas";
export interface TextData extends XYGlyphData {
    _text: Arrayable<string>;
    _angle: Arrayable<number>;
    _x_offset: Arrayable<number>;
    _y_offset: Arrayable<number>;
}
export interface TextView extends TextData {
}
export declare class TextView extends XYGlyphView {
    model: Text;
    visuals: Text.Visuals;
    protected _render(ctx: Context2d, indices: number[], {sx, sy, _x_offset, _y_offset, _angle, _text}: TextData): void;
}
export declare namespace Text {
    interface Mixins extends TextMixinVector {
    }
    interface Attrs extends XYGlyph.Attrs, Mixins {
        text: StringSpec;
        angle: AngleSpec;
        x_offset: NumberSpec;
        y_offset: NumberSpec;
    }
    interface Props extends XYGlyph.Props {
    }
    interface Visuals extends XYGlyph.Visuals {
        text: visuals.Text;
    }
}
export interface Text extends Text.Attrs {
}
export declare class Text extends XYGlyph {
    properties: Text.Props;
    constructor(attrs?: Partial<Text.Attrs>);
    static initClass(): void;
}
