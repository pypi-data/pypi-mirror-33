import { Widget } from '@phosphor/widgets';
import { ServiceManager, ContentsManager } from '@jupyterlab/services';
import { Toolbar } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { AngularWidget } from './phosphor-angular-loader';
import { AppComponent } from './app.component';
import { AppModule } from './app.module';
import { IScriptedForms } from './services/initialisation.service';
export declare namespace IScriptedFormsWidget {
    interface IOptions {
        serviceManager: ServiceManager;
        contentsManager: ContentsManager;
        context?: DocumentRegistry.Context;
    }
}
export declare namespace IAngularWrapperWidget {
    interface IOptions {
        toolbar: Toolbar<Widget>;
        serviceManager: ServiceManager;
        contentsManager: ContentsManager;
        context?: DocumentRegistry.Context;
    }
}
export declare class AngularWrapperWidget extends AngularWidget<AppComponent, AppModule> {
    scriptedFormsOptions: IScriptedForms.IOptions;
    constructor(options: IAngularWrapperWidget.IOptions);
    initiliseScriptedForms(): void;
    initiliseBaseScriptedForms(): void;
    setTemplateToString(dummyPath: string, template: string): void;
}
export declare class ScriptedFormsWidget extends Widget implements DocumentRegistry.IReadyWidget {
    _context: DocumentRegistry.Context;
    form: AngularWrapperWidget;
    id: 'ScriptedForms';
    constructor(options: IScriptedFormsWidget.IOptions);
    readonly ready: Promise<void>;
    readonly context: DocumentRegistry.Context;
    onPathChanged(): void;
    dispose(): void;
}
