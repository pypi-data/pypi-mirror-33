import { Range } from "./range";
export declare namespace Range1d {
    interface Attrs extends Range.Attrs {
        start: number;
        end: number;
    }
    interface Props extends Range.Props {
    }
}
export interface Range1d extends Range1d.Attrs {
}
export declare class Range1d extends Range {
    properties: Range1d.Props;
    constructor(attrs?: Partial<Range1d.Attrs>);
    static initClass(): void;
    protected _initial_start: number;
    protected _initial_end: number;
    protected _set_auto_bounds(): void;
    initialize(): void;
    readonly min: number;
    readonly max: number;
    readonly is_reversed: boolean;
    reset(): void;
}
