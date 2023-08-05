import { QueryList, AfterViewInit } from '@angular/core';
import { PromiseDelegate } from '@phosphor/coreutils';
import { CodeComponent } from '../code-module/code.component';
export declare class SectionBaseComponent implements AfterViewInit {
    onLoad?: string;
    code?: string;
    sectionId: number;
    sectionType: string;
    isFormReady: boolean;
    codeRunning: boolean;
    formReadyPromiseDelegate: PromiseDelegate<void>;
    viewInitPromiseDelegate: PromiseDelegate<void>;
    codeComponentsArray: CodeComponent[];
    contentCodeComponents: QueryList<CodeComponent>;
    viewCodeComponents: QueryList<CodeComponent>;
    ngAfterViewInit(): void;
    runCode(evenIfNotReady?: boolean): Promise<any>;
    _runAllCodeComponents(runCodeComplete: PromiseDelegate<null>): void;
    formReady(isReady: boolean): void;
    setId(id: number): void;
    kernelReset(): void;
}
