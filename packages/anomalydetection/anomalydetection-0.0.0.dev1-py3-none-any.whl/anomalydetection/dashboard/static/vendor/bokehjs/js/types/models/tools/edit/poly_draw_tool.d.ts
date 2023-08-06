import { UIEvent, GestureEvent, TapEvent, MoveEvent, KeyEvent } from "core/ui_events";
import { MultiLine } from "../../glyphs/multi_line";
import { Patches } from "../../glyphs/patches";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { EditTool, EditToolView } from "./edit_tool";
export interface HasPolyGlyph {
    glyph: MultiLine | Patches;
}
export declare class PolyDrawToolView extends EditToolView {
    model: PolyDrawTool;
    _drawing: boolean;
    _tap(ev: TapEvent): void;
    _draw(ev: UIEvent, mode: string): void;
    _doubletap(ev: TapEvent): void;
    _move(ev: MoveEvent): void;
    _remove(): void;
    _keyup(ev: KeyEvent): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    deactivate(): void;
}
export declare namespace PolyDrawTool {
    interface Attrs extends EditTool.Attrs {
        drag: boolean;
        renderers: (GlyphRenderer & HasPolyGlyph)[];
    }
    interface Props extends EditTool.Props {
    }
}
export interface PolyDrawTool extends PolyDrawTool.Attrs {
}
export declare class PolyDrawTool extends EditTool {
    properties: PolyDrawTool.Props;
    renderers: (GlyphRenderer & HasPolyGlyph)[];
    constructor(attrs?: Partial<PolyDrawTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: ("pan" | "tap" | "move")[];
    default_order: number;
}
