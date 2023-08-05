import { AfterViewInit, ElementRef, OnDestroy } from '@angular/core';
import { PromiseDelegate } from '@phosphor/coreutils';
import { RenderMimeRegistry } from '@jupyterlab/rendermime';
import { OutputArea, OutputAreaModel } from '@jupyterlab/outputarea';
import { Kernel } from '@jupyterlab/services';
import { KernelService } from '../services/kernel.service';
export declare class CodeComponent implements AfterViewInit, OnDestroy {
    private myKernelSevice;
    private _eRef;
    private _displayIdMap;
    name: string;
    renderMime: RenderMimeRegistry;
    model: OutputAreaModel;
    outputAreaOptions: OutputArea.IOptions;
    outputArea: OutputArea;
    promise: Promise<Kernel.IFuture>;
    outputContainer: HTMLDivElement;
    firstDisplay: PromiseDelegate<null>;
    code: string;
    codecontainer: ElementRef;
    constructor(myKernelSevice: KernelService, _eRef: ElementRef);
    updateOutputAreaModel(): void;
    ngAfterViewInit(): void;
    outputAreaDispose(): void;
    ngOnDestroy(): void;
    /**
     * Run the code within the code component. Update the output area with the results of the
     * code.
     */
    runCode(): Promise<null>;
    private _onIOPub;
}
