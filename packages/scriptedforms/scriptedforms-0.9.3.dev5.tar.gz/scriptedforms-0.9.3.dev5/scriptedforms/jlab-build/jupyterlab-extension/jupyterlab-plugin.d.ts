import { JupyterLabPlugin } from '@jupyterlab/application';
import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { ServiceManager, ContentsManager } from '@jupyterlab/services';
import { ScriptedFormsWidget } from './../app/widget';
export declare namespace IScriptedFormsWidgetFactory {
    interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
        serviceManager: ServiceManager;
        contentsManager: ContentsManager;
    }
}
export declare class ScriptedFormsWidgetFactory extends ABCWidgetFactory<ScriptedFormsWidget, DocumentRegistry.IModel> {
    serviceManager: ServiceManager;
    contentsManager: ContentsManager;
    constructor(options: IScriptedFormsWidgetFactory.IOptions);
    protected createNewWidget(context: DocumentRegistry.Context): ScriptedFormsWidget;
}
export declare const plugin: JupyterLabPlugin<void>;
