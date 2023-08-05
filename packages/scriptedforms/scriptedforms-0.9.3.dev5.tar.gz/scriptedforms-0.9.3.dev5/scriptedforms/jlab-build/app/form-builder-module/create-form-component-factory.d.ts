/**
 * Since the template for the form changes within the user interface
 * the form component needs to be re-compiled each time the template changes.
 *
 * This file exports a the `createFormComponentFactory` function which
 * creates a new form component factory based on the provided template.
 *
 * Within that function is the `FormComponent`. This component takes in the
 * provided template and then initialises the form.
 *
 * Form initialisation logic and ordering is all defined within the `initialiseForm`
 * function within the `FormComponent`.
 */
import { Component, Compiler, ComponentFactory } from '@angular/core';
import { PromiseDelegate } from '@phosphor/coreutils';
export interface IFormComponent {
    formViewInitialised: PromiseDelegate<void>;
    formReady: PromiseDelegate<void>;
    restartFormKernel(): Promise<void>;
}
/**
 * Create a form component factory given an Angular template in the form of metadata.
 *
 * @param compiler the Angular compiler
 * @param metadata the template containing metadata
 *
 * @returns a factory which creates form components
 */
export declare function createFormComponentFactory(compiler: Compiler, metadata: Component): ComponentFactory<IFormComponent>;
