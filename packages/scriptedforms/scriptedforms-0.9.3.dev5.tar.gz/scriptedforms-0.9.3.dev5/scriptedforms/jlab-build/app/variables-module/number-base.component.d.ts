import { AfterViewInit } from '@angular/core';
import { VariableBaseComponent } from './variable-base.component';
export declare class NumberBaseComponent extends VariableBaseComponent implements AfterViewInit {
    min?: number;
    max?: number;
    step?: number;
    usedSeparator: boolean;
    loadVariableName(): void;
}
