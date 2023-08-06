import { GestureEvent, TapEvent, MoveEvent, KeyEvent } from "core/ui_events";
import { MultiLine } from "../../glyphs/multi_line";
import { Patches } from "../../glyphs/patches";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { EditTool, EditToolView, HasXYGlyph } from "./edit_tool";
export interface HasPolyGlyph {
    glyph: MultiLine | Patches;
}
export declare class PolyEditToolView extends EditToolView {
    model: PolyEditTool;
    _selected_renderer: GlyphRenderer | null;
    _basepoint: [number, number] | null;
    _drawing: boolean;
    _doubletap(ev: TapEvent): void;
    _move(ev: MoveEvent): void;
    _tap(ev: TapEvent): void;
    _remove_vertex(emit?: boolean): void;
    _pan_start(ev: GestureEvent): void;
    _pan(ev: GestureEvent): void;
    _pan_end(_e: GestureEvent): void;
    _keyup(ev: KeyEvent): void;
    deactivate(): void;
}
export declare namespace PolyEditTool {
    interface Attrs extends EditTool.Attrs {
        vertex_renderer: (GlyphRenderer & HasXYGlyph);
        renderers: (GlyphRenderer & HasPolyGlyph)[];
    }
    interface Props extends EditTool.Props {
    }
}
export interface PolyEditTool extends PolyEditTool.Attrs {
}
export declare class PolyEditTool extends EditTool {
    properties: PolyEditTool.Props;
    renderers: (GlyphRenderer & HasPolyGlyph)[];
    constructor(attrs?: Partial<PolyEditTool.Attrs>);
    static initClass(): void;
    tool_name: string;
    icon: string;
    event_type: ("pan" | "tap" | "move")[];
    default_order: number;
}
