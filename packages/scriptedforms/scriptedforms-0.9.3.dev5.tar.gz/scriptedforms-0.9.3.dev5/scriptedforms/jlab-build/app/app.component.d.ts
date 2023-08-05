import { AfterViewInit, ElementRef, ChangeDetectorRef } from '@angular/core';
import { Kernel } from '@jupyterlab/services';
import { FormBuilderComponent } from './form-builder-module/form-builder.component';
import { IScriptedForms, InitialisationService } from './services/initialisation.service';
import { FormService } from './services/form.service';
import { KernelService } from './services/kernel.service';
import { VariableService } from './services/variable.service';
import { FileService } from './services/file.service';
import { FormStatus } from './types/form-status';
export declare class AppComponent implements AfterViewInit {
    private myFileService;
    private myFormService;
    private myInitialisationService;
    private myKernelSevice;
    private myVariableService;
    private myChangeDetectorRef;
    kernelStatus: Kernel.Status;
    formStatus: FormStatus;
    variableStatus: string;
    queueLength: number;
    formBuilderComponent: FormBuilderComponent;
    jupyterErrorMsg: ElementRef;
    constructor(myFileService: FileService, myFormService: FormService, myInitialisationService: InitialisationService, myKernelSevice: KernelService, myVariableService: VariableService, myChangeDetectorRef: ChangeDetectorRef);
    ngAfterViewInit(): void;
    initiliseScriptedForms(options: IScriptedForms.IOptions): void;
    initiliseBaseScriptedForms(options: IScriptedForms.IOptions): void;
    setTemplateToString(dummyPath: string, template: string): void;
}
