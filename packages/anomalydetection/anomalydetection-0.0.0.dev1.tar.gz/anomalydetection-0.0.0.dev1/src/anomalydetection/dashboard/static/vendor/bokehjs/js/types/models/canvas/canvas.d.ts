import { LayoutCanvas } from "core/layout/layout_canvas";
import { DOMView } from "core/dom_view";
import { Constraint } from "core/layout/solver";
import { OutputBackend } from "core/enums";
import { Context2d } from "core/util/canvas";
export declare class CanvasView extends DOMView {
    model: Canvas;
    private _ctx;
    ctx: Context2d;
    canvas_el: HTMLCanvasElement;
    overlays_el: HTMLElement;
    events_el: HTMLElement;
    map_el: HTMLElement | null;
    protected _width_constraint: Constraint | undefined;
    protected _height_constraint: Constraint | undefined;
    initialize(options: any): void;
    css_classes(): string[];
    get_ctx(): Context2d;
    get_canvas_element(): HTMLCanvasElement;
    prepare_canvas(): void;
    set_dims([width, height]: [number, number]): void;
}
export declare namespace Canvas {
    interface Attrs extends LayoutCanvas.Attrs {
        map: boolean;
        use_hidpi: boolean;
        pixel_ratio: number;
        output_backend: OutputBackend;
    }
    interface Props extends LayoutCanvas.Props {
    }
}
export interface Canvas extends Canvas.Attrs {
}
export declare class Canvas extends LayoutCanvas {
    properties: Canvas.Props;
    constructor(attrs?: Partial<Canvas.Attrs>);
    static initClass(): void;
    readonly panel: LayoutCanvas;
}
