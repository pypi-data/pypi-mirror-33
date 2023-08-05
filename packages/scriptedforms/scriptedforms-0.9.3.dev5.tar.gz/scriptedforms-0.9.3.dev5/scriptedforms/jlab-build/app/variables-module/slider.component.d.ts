import { AfterViewInit } from '@angular/core';
import { NumberBaseComponent } from './number-base.component';
export declare class SliderComponent extends NumberBaseComponent implements AfterViewInit {
    min?: number;
    max?: number;
    updateValue(value: number): void;
}
