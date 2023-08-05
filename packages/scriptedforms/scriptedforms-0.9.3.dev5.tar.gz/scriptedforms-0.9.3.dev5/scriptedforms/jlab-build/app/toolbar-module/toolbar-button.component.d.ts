import { BehaviorSubject, Subscription } from 'rxjs';
import { ElementRef } from '@angular/core';
export interface IOptions {
    click?: () => void;
    href?: string;
    icon?: string;
    disable?: BehaviorSubject<boolean>;
    tooltip?: string;
}
export declare class ToolbarButtonComponent {
    myElementRef: ElementRef;
    _options: IOptions;
    options: IOptions;
    button: ElementRef;
    previousSubscription: Subscription;
    isDisabled: boolean;
    constructor(myElementRef: ElementRef);
}
