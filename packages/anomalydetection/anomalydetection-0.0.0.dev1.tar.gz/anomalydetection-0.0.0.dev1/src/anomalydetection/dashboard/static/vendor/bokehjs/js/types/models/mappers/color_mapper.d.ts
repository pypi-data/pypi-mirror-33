import { Transform } from "../transforms/transform";
import { Factor } from "../ranges/factor_range";
import { Arrayable, Color } from "core/types";
export interface RGBAMapper {
    v_compute(xs: Arrayable<number> | Arrayable<Factor>): Uint8Array;
}
export declare function _convert_color(color: string): number;
export declare function _convert_palette(palette: Color[]): Uint32Array;
export declare function _uint32_to_rgba(values: Uint32Array): Uint8Array;
export declare namespace ColorMapper {
    interface Attrs extends Transform.Attrs {
        palette: Color[];
        nan_color: Color;
    }
    interface Props extends Transform.Props {
    }
}
export interface ColorMapper extends ColorMapper.Attrs {
}
export declare abstract class ColorMapper extends Transform<Color> {
    properties: ColorMapper.Props;
    constructor(attrs?: Partial<ColorMapper.Attrs>);
    static initClass(): void;
    compute(_x: number): never;
    v_compute(xs: Arrayable<number> | Arrayable<Factor>): Arrayable<Color>;
    readonly rgba_mapper: RGBAMapper;
    protected _colors<T>(conv: (c: Color) => T): {
        nan_color: T;
    };
    protected abstract _v_compute<T>(xs: Arrayable<number> | Arrayable<Factor>, values: Arrayable<T>, palette: Arrayable<T>, colors: {
        nan_color: T;
    }): void;
}
