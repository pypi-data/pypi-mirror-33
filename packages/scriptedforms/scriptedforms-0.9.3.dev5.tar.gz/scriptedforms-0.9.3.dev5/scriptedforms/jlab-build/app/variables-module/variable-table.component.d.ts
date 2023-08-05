import { AfterViewInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material';
import { VariableBaseComponent } from './variable-base.component';
import { PandasTable } from '../interfaces/pandas-table';
import { VariableParameterComponent } from './variable-parameter.component';
export declare class VariableTableComponent extends VariableBaseComponent implements AfterViewInit {
    typeEdit?: string;
    inputTypes?: string;
    dropdownItems?: string;
    variableInputTypes: VariableParameterComponent;
    variableDropdownItems: VariableParameterComponent;
    definedInputTypes: {};
    definedDropdownItems: {};
    tableIndex: (string | number)[];
    availableTypes: string[];
    types: string[];
    columnDefs: (string | number)[];
    oldColumnDefs: (string | number)[];
    dataSource: MatTableDataSource<{
        [key: string]: string | number;
    }>;
    variableValue: PandasTable;
    oldVariableValue: PandasTable;
    isPandas: boolean;
    focus: [number, string];
    ngAfterViewInit(): void;
    updateVariableView(value: PandasTable): void;
    dataChanged(): void;
    typesChanged(): void;
    testIfDifferent(): boolean;
    pythonValueReference(): string;
    pythonVariableEvaluate(): string;
    onBlur(tableCoords: [number, string]): void;
    onFocus(tableCoords: [number, string]): void;
}
