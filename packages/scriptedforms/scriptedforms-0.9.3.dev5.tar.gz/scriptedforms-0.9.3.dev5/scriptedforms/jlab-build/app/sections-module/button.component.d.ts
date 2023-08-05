import { AfterViewInit, ElementRef } from '@angular/core';
import { SectionBaseComponent } from './section-base.component';
import { ConditionalComponent } from '../variables-module/conditional.component';
export declare class ButtonComponent extends SectionBaseComponent implements AfterViewInit {
    myElementRef: ElementRef;
    sectionType: string;
    inline?: string;
    conditional?: string;
    conditionalValue: boolean;
    conditionalComponent: ConditionalComponent;
    value?: string;
    name: string;
    constructor(myElementRef: ElementRef);
    ngAfterViewInit(): void;
}
