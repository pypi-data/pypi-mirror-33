import { Subscription } from 'rxjs';
import { OnDestroy, AfterViewInit } from '@angular/core';
import { SectionBaseComponent } from './section-base.component';
import { VariableService } from '../services/variable.service';
export declare class OutputComponent extends SectionBaseComponent implements OnDestroy, AfterViewInit {
    private myVariableService;
    sectionType: string;
    variableSubscription: Subscription;
    hasFirstSubRun: boolean;
    constructor(myVariableService: VariableService);
    subscribeToVariableChanges(): void;
    unsubscribe(): void;
    kernelReset(): void;
    ngOnDestroy(): void;
}
