import { VariableBaseComponent } from './variable-base.component';
import { AfterViewInit } from '@angular/core';
export declare class StringComponent extends VariableBaseComponent implements AfterViewInit {
    variableValue: string;
    pythonValueReference(): string;
}
