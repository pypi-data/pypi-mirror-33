"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version (the "AGPL-3.0+").
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License and the additional terms for more
// details.
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
// ADDITIONAL TERMS are also included as allowed by Section 7 of the GNU
// Affrero General Public License. These aditional terms are Sections 1, 5,
// 6, 7, 8, and 9 from the Apache License, Version 2.0 (the "Apache-2.0")
// where all references to the definition "License" are instead defined to
// mean the AGPL-3.0+.
// You should have received a copy of the Apache-2.0 along with this
// program. If not, see <http://www.apache.org/licenses/LICENSE-2.0>.
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
var core_1 = require("@angular/core");
var common_1 = require("@angular/common");
var forms_1 = require("@angular/forms");
var coreutils_1 = require("@phosphor/coreutils");
var material_module_1 = require("../../vendors/material.module");
var session_start_code_1 = require("./session-start-code");
var kernel_service_1 = require("../services/kernel.service");
var variable_service_1 = require("../services/variable.service");
var sections_module_1 = require("../sections-module/sections.module");
var start_component_1 = require("../sections-module/start.component");
var live_component_1 = require("../sections-module/live.component");
var button_component_1 = require("../sections-module/button.component");
var output_component_1 = require("../sections-module/output.component");
var section_file_change_component_1 = require("../sections-module/section-file-change.component");
var variables_module_1 = require("../variables-module/variables.module");
var toggle_component_1 = require("../variables-module/toggle.component");
var tick_component_1 = require("../variables-module/tick.component");
var number_component_1 = require("../variables-module/number.component");
var slider_component_1 = require("../variables-module/slider.component");
var variable_table_component_1 = require("../variables-module/variable-table.component");
var string_component_1 = require("../variables-module/string.component");
var dropdown_component_1 = require("../variables-module/dropdown.component");
var variable_file_component_1 = require("../variables-module/variable-file.component");
var code_module_1 = require("../code-module/code.module");
var code_component_1 = require("../code-module/code.component");
/**
 * Create a form component factory given an Angular template in the form of metadata.
 *
 * @param compiler the Angular compiler
 * @param metadata the template containing metadata
 *
 * @returns a factory which creates form components
 */
function createFormComponentFactory(compiler, metadata) {
    /**
     * The form component that is built each time the template changes
     */
    var FormComponent = /** @class */ (function () {
        function FormComponent(myKernelService, myVariableService, myChangeDetectorRef) {
            this.myKernelService = myKernelService;
            this.myVariableService = myVariableService;
            this.myChangeDetectorRef = myChangeDetectorRef;
            this.formViewInitialised = new coreutils_1.PromiseDelegate();
            this.formReady = new coreutils_1.PromiseDelegate();
            this.variableComponents = [];
            this.sectionComponents = [];
        }
        FormComponent.prototype.ngAfterViewInit = function () {
            var _this = this;
            this.formViewInitialised.resolve(null);
            this.variableComponents = this.variableComponents.concat(this.toggleComponents.toArray());
            this.variableComponents = this.variableComponents.concat(this.tickComponents.toArray());
            this.buttonComponents.toArray().forEach(function (buttonComponent) {
                if (buttonComponent.conditional) {
                    _this.variableComponents = _this.variableComponents.concat([buttonComponent.conditionalComponent]);
                }
            });
            this.variableComponents = this.variableComponents.concat(this.numberComponents.toArray());
            this.variableComponents = this.variableComponents.concat(this.sliderComponents.toArray());
            this.variableComponents = this.variableComponents.concat(this.variableTableComponents.toArray());
            this.variableTableComponents.toArray().forEach(function (variableTableComponent) {
                if (variableTableComponent.inputTypes) {
                    _this.variableComponents = _this.variableComponents.concat([variableTableComponent.variableInputTypes]);
                }
                if (variableTableComponent.dropdownItems) {
                    _this.variableComponents = _this.variableComponents.concat([variableTableComponent.variableDropdownItems]);
                }
            });
            this.variableComponents = this.variableComponents.concat(this.stringComponents.toArray());
            this.variableComponents = this.variableComponents.concat(this.dropdownComponents.toArray());
            this.dropdownComponents.toArray().forEach(function (dropdownComponent) {
                if (dropdownComponent.items) {
                    _this.variableComponents = _this.variableComponents.concat([dropdownComponent.variableParameterComponent]);
                }
            });
            this.variableComponents = this.variableComponents.concat(this.variableFileComponents.toArray());
            this.sectionComponents = this.sectionComponents.concat(this.startComponents.toArray());
            this.sectionComponents = this.sectionComponents.concat(this.liveComponents.toArray());
            this.sectionComponents = this.sectionComponents.concat(this.buttonComponents.toArray());
            this.sectionComponents = this.sectionComponents.concat(this.outputComponents.toArray());
            this.sectionComponents = this.sectionComponents.concat(this.sectionFileChangeComponents.toArray());
            this.sectionFileChangeComponents.toArray().forEach(function (sectionFileChangeComponent) {
                _this.variableComponents = _this.variableComponents.concat([sectionFileChangeComponent.variableParameterComponent]);
            });
            this.sectionComponents.forEach(function (sectionComponent, index) {
                sectionComponent.setId(index);
            });
            this.variableComponents.forEach(function (variableComponent, index) {
                variableComponent.setId(index);
            });
            this.myChangeDetectorRef.detectChanges();
            this.initialiseForm();
        };
        /**
         * Initialise the form. Code ordering during initialisation is defined here.
         */
        FormComponent.prototype.initialiseForm = function () {
            var _this = this;
            this.myVariableService.resetVariableService();
            this.myKernelService.queueReset();
            var sessionStartCodeComplete = new coreutils_1.PromiseDelegate();
            this.myKernelService.runCode(session_start_code_1.sessionStartCode, '"session_start_code"')
                .then(function (future) {
                if (future) {
                    var textContent_1 = '';
                    future.onIOPub = (function (msg) {
                        if (msg.content.text) {
                            textContent_1 = textContent_1.concat(String(msg.content.text));
                        }
                    });
                    future.done.then(function () { return sessionStartCodeComplete.resolve(JSON.parse(textContent_1)); });
                }
            });
            sessionStartCodeComplete.promise.then(function (isNewSession) {
                if (isNewSession) {
                    console.log('Restoring old session');
                }
                else {
                    console.log('Starting a new session');
                }
                _this.variableComponents.forEach(function (variableComponent, index) {
                    variableComponent.initialise();
                });
                _this.myVariableService.startListeningForChanges();
                _this.myVariableService.allVariablesInitilised().then(function () {
                    var initialPromise = Promise.resolve(null);
                    var startPromiseList = [initialPromise];
                    _this.startComponents.toArray().forEach(function (startComponent, index) {
                        // console.log(startComponent);
                        if (isNewSession) {
                            startPromiseList.push(startPromiseList[startPromiseList.length - 1].then(function () { return startComponent.runCode(); }));
                        }
                        else if (startComponent.always === '') {
                            startPromiseList.push(startPromiseList[startPromiseList.length - 1].then(function () { return startComponent.runCode(); }));
                        }
                    });
                    return Promise.all(startPromiseList);
                }).then(function () {
                    var initialPromise = Promise.resolve(null);
                    var sectionPromiseList = [initialPromise];
                    _this.sectionComponents.forEach(function (sectionComponent) {
                        if (sectionComponent.onLoad === '') {
                            sectionPromiseList.push(sectionPromiseList[sectionPromiseList.length - 1].then(function () { return sectionComponent.runCode(); }));
                        }
                    });
                    // Wait until the code queue is complete before declaring form ready to
                    // the various components.
                    return Promise.all(sectionPromiseList);
                })
                    .then(function () {
                    _this.liveComponents.toArray().forEach(function (liveComponent) { return liveComponent.subscribe(); });
                    _this.outputComponents.toArray().forEach(function (outputComponent) { return outputComponent.subscribeToVariableChanges(); });
                    _this.sectionComponents.forEach(function (sectionComponent) { return sectionComponent.formReady(true); });
                    _this.variableComponents.forEach(function (variableComponent) { return variableComponent.formReady(true); });
                    _this.formReady.resolve(null);
                });
            });
        };
        FormComponent.prototype.restartFormKernel = function () {
            var _this = this;
            this.formReady = new coreutils_1.PromiseDelegate();
            this.variableComponents.forEach(function (variableComponent) {
                variableComponent.variableValue = null;
                variableComponent.formReady(false);
            });
            this.sectionComponents.forEach(function (sectionComponent) {
                sectionComponent.kernelReset();
                sectionComponent.formReady(false);
            });
            this.myKernelService.restartKernel().then(function () {
                _this.initialiseForm();
            });
            return this.formReady.promise;
        };
        __decorate([
            core_1.ViewChildren(start_component_1.StartComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "startComponents", void 0);
        __decorate([
            core_1.ViewChildren(live_component_1.LiveComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "liveComponents", void 0);
        __decorate([
            core_1.ViewChildren(button_component_1.ButtonComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "buttonComponents", void 0);
        __decorate([
            core_1.ViewChildren(output_component_1.OutputComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "outputComponents", void 0);
        __decorate([
            core_1.ViewChildren(section_file_change_component_1.SectionFileChangeComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "sectionFileChangeComponents", void 0);
        __decorate([
            core_1.ViewChildren(toggle_component_1.ToggleComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "toggleComponents", void 0);
        __decorate([
            core_1.ViewChildren(tick_component_1.TickComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "tickComponents", void 0);
        __decorate([
            core_1.ViewChildren(number_component_1.NumberComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "numberComponents", void 0);
        __decorate([
            core_1.ViewChildren(slider_component_1.SliderComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "sliderComponents", void 0);
        __decorate([
            core_1.ViewChildren(variable_table_component_1.VariableTableComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "variableTableComponents", void 0);
        __decorate([
            core_1.ViewChildren(string_component_1.StringComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "stringComponents", void 0);
        __decorate([
            core_1.ViewChildren(dropdown_component_1.DropdownComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "dropdownComponents", void 0);
        __decorate([
            core_1.ViewChildren(variable_file_component_1.VariableFileComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "variableFileComponents", void 0);
        __decorate([
            core_1.ViewChildren(code_component_1.CodeComponent),
            __metadata("design:type", core_1.QueryList)
        ], FormComponent.prototype, "codeComponents", void 0);
        FormComponent = __decorate([
            core_1.Component(metadata),
            __metadata("design:paramtypes", [kernel_service_1.KernelService,
                variable_service_1.VariableService,
                core_1.ChangeDetectorRef])
        ], FormComponent);
        return FormComponent;
    }());
    // The Angular module for the form component
    var FormComponentModule = /** @class */ (function () {
        function FormComponentModule() {
        }
        FormComponentModule = __decorate([
            core_1.NgModule({
                imports: [
                    common_1.CommonModule,
                    forms_1.FormsModule,
                    material_module_1.MaterialModule,
                    sections_module_1.SectionsModule,
                    variables_module_1.VariablesModule,
                    code_module_1.CodeModule
                ],
                declarations: [
                    FormComponent
                ]
            })
        ], FormComponentModule);
        return FormComponentModule;
    }());
    // Compile the template
    var module = (compiler.compileModuleAndAllComponentsSync(FormComponentModule));
    // Return the factory
    return module.componentFactories.find(function (f) { return f.componentType === FormComponent; });
}
exports.createFormComponentFactory = createFormComponentFactory;
//# sourceMappingURL=create-form-component-factory.js.map