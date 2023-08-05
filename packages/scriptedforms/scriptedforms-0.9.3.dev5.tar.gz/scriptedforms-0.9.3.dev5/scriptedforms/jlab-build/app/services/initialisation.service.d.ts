import { Widget } from '@phosphor/widgets';
import { ServiceManager, ContentsManager } from '@jupyterlab/services';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { Toolbar } from '@jupyterlab/apputils';
import { JupyterService } from './jupyter.service';
import { WatchdogService } from './watchdog.service';
import { FileService } from './file.service';
import { ToolbarService } from './toolbar.service';
export declare namespace IScriptedForms {
    interface IOptions {
        serviceManager: ServiceManager;
        contentsManager: ContentsManager;
        node: HTMLElement;
        toolbar: Toolbar<Widget>;
        context?: DocumentRegistry.Context;
    }
}
export declare class InitialisationService {
    private myJupyterService;
    private myFileService;
    private myWatchdogService;
    private myToolbarService;
    constructor(myJupyterService: JupyterService, myFileService: FileService, myWatchdogService: WatchdogService, myToolbarService: ToolbarService);
    initiliseBaseScriptedForms(options: IScriptedForms.IOptions): void;
    initiliseScriptedForms(options: IScriptedForms.IOptions): void;
}
