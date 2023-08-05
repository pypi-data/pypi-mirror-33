import { Subscription, BehaviorSubject } from 'rxjs';
import { nbformat } from '@jupyterlab/coreutils';
import { KernelService } from './kernel.service';
import { VariableStore } from '../interfaces/variable-store';
import { VariableValue } from '../types/variable-value';
import { VariableComponent } from '../types/variable-component';
export declare class VariableService {
    private myKernelSevice;
    variableHandlerClass: string;
    handlerName: string;
    fetchVariablesCode: string;
    variableStore: BehaviorSubject<VariableStore>;
    oldVariableStore: VariableStore;
    variableIdentifierMap: {
        [key: string]: string;
    };
    variableEvaluateMap: {
        [key: string]: string;
    };
    pythonVariables: VariableStore;
    variableChangedObservable: BehaviorSubject<VariableStore>;
    variableComponentStore: {
        [key: string]: VariableComponent;
    };
    executionCount: BehaviorSubject<nbformat.ExecutionCount>;
    lastCode: BehaviorSubject<string>;
    variableChangeSubscription: Subscription;
    variableStatus: BehaviorSubject<string>;
    variableHandlerInitialised: boolean;
    constructor(myKernelSevice: KernelService);
    variableInitialisation(): void;
    startListeningForChanges(): void;
    resetVariableService(): void;
    allVariablesInitilised(): Promise<void>;
    appendToIdentifierMap(variableIdentifier: string, variableName: string): void;
    appendToEvaluateMap(variableName: string, variableEvaluate: string): void;
    initialiseVariableComponent(component: VariableComponent): void;
    convertToVariableStore(textContent: string): void;
    ifJsonString(string: string): boolean;
    fetchAll(label?: string): Promise<any>;
    updateComponentView(component: any, value: VariableValue): void;
    variableHasChanged(identifier: string): void;
    checkForChanges(): void;
    pushVariable(variableIdentifier: string, variableName: string, valueReference: string): Promise<any>;
}
