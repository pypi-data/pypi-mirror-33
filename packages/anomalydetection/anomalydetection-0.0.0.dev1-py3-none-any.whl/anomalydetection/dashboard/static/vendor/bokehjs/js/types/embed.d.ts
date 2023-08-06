import { Document, DocJson } from "./document";
import { Receiver } from "./protocol/receiver";
import { DOMView } from "./core/dom_view";
export declare type DocsJson = {
    [key: string]: DocJson;
};
export interface RenderItem {
    elementid: string;
    docid?: string;
    modelid?: string;
    sessionid?: string;
    use_for_title?: boolean;
    notebook_comms_target?: any;
}
export interface CommMessage {
    buffers: DataView[];
    content: {
        data: string;
    };
}
export interface Comm {
    target_name: string;
    on_msg: (msg: CommMessage) => void;
    onMsg: (this: Document, receiver: Receiver, comm_msg: CommMessage) => void;
}
export interface Kernel {
    comm_manager: {
        register_target: (target: string, fn: (comm: Comm) => void) => void;
    };
    registerCommTarget: (target: string, fn: (comm: Comm) => void) => void;
}
export declare const kernels: {
    [key: string]: Kernel;
};
export declare const BOKEH_ROOT = "bk-root";
export declare function add_model_standalone(model_id: string, element: HTMLElement, doc: Document): DOMView;
export declare function add_document_standalone(document: Document, element: HTMLElement, use_for_title?: boolean): {
    [key: string]: DOMView;
};
export declare function add_document_from_session(element: HTMLElement, websocket_url: string, session_id: string, use_for_title: boolean): Promise<{
    [key: string]: DOMView;
}>;
export declare function add_model_from_session(element: HTMLElement, websocket_url: string, model_id: string, session_id: string): Promise<DOMView>;
export declare function inject_css(url: string): void;
export declare function inject_raw_css(css: string): void;
export declare function embed_items_notebook(docs_json: DocsJson, render_items: RenderItem[]): void;
export declare function embed_items(docs_json: string | DocsJson, render_items: RenderItem[], app_path?: string, absolute_url?: string): void;
