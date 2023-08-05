import { Widget } from '@phosphor/widgets';
import { PromiseDelegate } from '@phosphor/coreutils';
import { Type, ComponentRef, NgZone, NgModuleRef } from '@angular/core';
export declare class AngularLoader<M> {
    private applicationRef;
    private componentFactoryResolver;
    ngZone: NgZone;
    private injector;
    constructor(ngModuleRef: NgModuleRef<M>);
    attachComponent<T>(ngComponent: Type<T>, dom: Element): ComponentRef<T>;
}
export declare class AngularWidget<C, M> extends Widget {
    angularLoader: AngularLoader<M>;
    ngZone: NgZone;
    componentRef: ComponentRef<C>;
    componentInstance: C;
    componentReady: PromiseDelegate<void>;
    constructor(ngComponent: Type<C>, ngModule: Type<M>, options?: Widget.IOptions);
    run(func: () => void): void;
    dispose(): void;
}
