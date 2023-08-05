import { AfterViewInit } from '@angular/core';
import { VariableBaseComponent } from './variable-base.component';
import { VariableParameterComponent } from './variable-parameter.component';
export declare class DropdownComponent extends VariableBaseComponent implements AfterViewInit {
    deprecatedOptions: (string | number)[];
    options: (string | number)[];
    usedSeparator: boolean;
    items?: string;
    variableParameterComponent: VariableParameterComponent;
    pythonValueReference(): string;
    loadVariableName(): void;
}
