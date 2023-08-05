import { Widget } from '@phosphor/widgets';
import { Toolbar } from '@jupyterlab/apputils';
import { PromiseDelegate } from '@phosphor/coreutils';
export declare class ToolbarService {
    toolbarReady: PromiseDelegate<void>;
    toolbar: Toolbar<Widget>;
    setToolbar(toolbar: Toolbar<Widget>): void;
    addSpacer(): void;
    addItem(name: string, widget: Widget): void;
}
