import { BehaviorSubject } from 'rxjs';
import { ComponentFactoryResolver, AfterViewInit, ComponentFactory, ViewContainerRef, ChangeDetectorRef } from '@angular/core';
import { ToolbarButtonComponent, IOptions } from './toolbar-button.component';
import { ToolbarService } from '../services/toolbar.service';
import { FormService } from '../services/form.service';
export declare class ToolbarBaseComponent implements AfterViewInit {
    private myComponentFactoryResolver;
    private myToolbarService;
    private myFormService;
    private changeDetectorRef;
    restartingKernel: BehaviorSubject<boolean>;
    container: ViewContainerRef;
    buttonFactory: ComponentFactory<ToolbarButtonComponent>;
    constructor(myComponentFactoryResolver: ComponentFactoryResolver, myToolbarService: ToolbarService, myFormService: FormService, changeDetectorRef: ChangeDetectorRef);
    ngAfterViewInit(): void;
    addButton(options: IOptions): void;
    restartKernel(): void;
}
