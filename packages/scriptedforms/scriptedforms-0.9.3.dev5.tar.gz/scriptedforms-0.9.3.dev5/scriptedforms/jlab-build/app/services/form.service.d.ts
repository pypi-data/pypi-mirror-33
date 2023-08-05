import { BehaviorSubject } from 'rxjs';
import { IFormComponent } from '../form-builder-module/create-form-component-factory';
import { FormBuilderComponent } from '../form-builder-module/form-builder.component';
import { FormStatus } from '../types/form-status';
export declare class FormService {
    template: BehaviorSubject<string>;
    component: IFormComponent;
    formBuilderComponent: FormBuilderComponent;
    initialising: FormStatus;
    formStatus: BehaviorSubject<FormStatus>;
    formInitialisation(): void;
    restartFormKernel(): Promise<void>;
    setTemplate(template: string): void;
    getTemplate(): string;
}
