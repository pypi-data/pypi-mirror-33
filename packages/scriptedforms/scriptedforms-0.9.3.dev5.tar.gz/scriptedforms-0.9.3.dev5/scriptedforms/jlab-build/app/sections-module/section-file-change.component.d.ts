import { Subscription } from 'rxjs';
import { OnDestroy, AfterViewInit } from '@angular/core';
import { SectionBaseComponent } from './section-base.component';
import { VariableParameterComponent } from '../variables-module/variable-parameter.component';
import { WatchdogService } from '../services/watchdog.service';
export declare class SectionFileChangeComponent extends SectionBaseComponent implements OnDestroy, AfterViewInit {
    private myWatchdogService;
    sectionType: string;
    watchdogSubscription: Subscription;
    pathsConverted: string[];
    paths: string;
    variableParameterComponent: VariableParameterComponent;
    constructor(myWatchdogService: WatchdogService);
    updateFilepathObserver(): void;
    ngAfterViewInit(): void;
    ngOnDestroy(): void;
}
