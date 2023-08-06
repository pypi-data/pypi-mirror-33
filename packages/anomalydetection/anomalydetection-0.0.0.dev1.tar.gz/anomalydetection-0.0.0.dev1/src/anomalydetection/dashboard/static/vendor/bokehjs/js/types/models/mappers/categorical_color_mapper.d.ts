import { ColorMapper } from "./color_mapper";
import { Factor } from "../ranges/factor_range";
import { Arrayable } from "core/types";
export declare namespace CategoricalColorMapper {
    interface Attrs extends ColorMapper.Attrs {
        factors: string[];
        start: number;
        end: number;
    }
    interface Props extends ColorMapper.Props {
    }
}
export interface CategoricalColorMapper extends CategoricalColorMapper.Attrs {
}
export declare class CategoricalColorMapper extends ColorMapper {
    properties: CategoricalColorMapper.Props;
    constructor(attrs?: Partial<CategoricalColorMapper.Attrs>);
    static initClass(): void;
    protected _v_compute<T>(data: Arrayable<Factor>, values: Arrayable<T>, palette: Arrayable<T>, {nan_color}: {
        nan_color: T;
    }): void;
}
