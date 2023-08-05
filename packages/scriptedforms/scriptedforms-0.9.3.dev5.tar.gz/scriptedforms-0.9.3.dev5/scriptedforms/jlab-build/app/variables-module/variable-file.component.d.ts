import { VariableBaseComponent } from './variable-base.component';
import { AfterViewInit, OnInit } from '@angular/core';
export declare class VariableFileComponent extends VariableBaseComponent implements OnInit, AfterViewInit {
    variableValue: number[];
    reader: FileReader;
    ngOnInit(): void;
    fileChanged(event: any): void;
    onFileLoaded(): void;
    pythonValueReference(): string;
    pythonVariableEvaluate(): string;
}
