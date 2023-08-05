"use strict";
/*
 *  Copyright 2017 Simon Biggs
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
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
var core_1 = require("@angular/core");
var form_builder_component_1 = require("./form-builder-module/form-builder.component");
var initialisation_service_1 = require("./services/initialisation.service");
var form_service_1 = require("./services/form.service");
var kernel_service_1 = require("./services/kernel.service");
var variable_service_1 = require("./services/variable.service");
var file_service_1 = require("./services/file.service");
/*
 *  # Create your own Angular JupyterLab extension (cont.)
 *
 *  This is part of the guide available at
 *  <https://github.com/SimonBiggs/scriptedforms/blob/master/scriptedforms/docs/create-your-own-angular-jupyterlab-extension.md>
 *
 *  ## The Root Angular App Component
 *
 *  There's a lot going on in this file, but the greater majority of its content
 *  is ScriptedForms specific. There are only two things you will need from this
 *  file.
 *
 *  The first is how the template is defined. The key part is the 'html-loader!'.
 *  JupyterLab does not have a webpack method for loading up Angular templates.
 *  This loader text tells the JupyterLab webpack that it needs to use the html-loader.
 *  So that typescript doesn't complain about this import a module type needs
 *  to be defined. This is done in [component-html.d.ts](../component-html.d.ts).
 *
 *  The last feature that is worth noting are the public functions provided at
 *  the bottom of AppComponent such as `initiliseScriptedForms`.
 *  These functions are passed up to the Phosphor Widget
 *  and are called using the AngularWidget run() function.
 */
// JupyterLab doesn't have custom webpack loaders. Need to be able to
// inline the loaders so that they get picked up without having access to the
// webpack.config.js file
// See https://github.com/jupyterlab/jupyterlab/pull/4334#issuecomment-383104318
var htmlTemplate = require("html-loader!./app.component.html");
// This is currently needed to silence the angular-language-service not finding
// a template for this component.
// See https://github.com/angular/angular/issues/23478
var linterWorkaroundHtmlTemplate = '' + htmlTemplate;
var AppComponent = /** @class */ (function () {
    function AppComponent(myFileService, myFormService, myInitialisationService, myKernelSevice, myVariableService, myChangeDetectorRef) {
        this.myFileService = myFileService;
        this.myFormService = myFormService;
        this.myInitialisationService = myInitialisationService;
        this.myKernelSevice = myKernelSevice;
        this.myVariableService = myVariableService;
        this.myChangeDetectorRef = myChangeDetectorRef;
        this.kernelStatus = 'unknown';
        this.formStatus = null;
        this.variableStatus = null;
        this.queueLength = null;
    }
    AppComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        this.myFormService.formBuilderComponent = this.formBuilderComponent;
        this.myFormService.formStatus.subscribe(function (status) {
            console.log('form: ' + status);
            _this.formStatus = status;
            _this.myChangeDetectorRef.detectChanges();
        });
        this.myVariableService.variableStatus.subscribe(function (status) {
            console.log('variable: ' + status);
            _this.variableStatus = status;
            _this.myChangeDetectorRef.detectChanges();
        });
        this.myKernelSevice.kernelStatus.subscribe(function (status) {
            console.log('kernel: ' + status);
            _this.kernelStatus = status;
            _this.myChangeDetectorRef.detectChanges();
        });
        this.myKernelSevice.queueLength.subscribe(function (length) {
            console.log('queue-length: ' + length);
            _this.queueLength = length;
            _this.myChangeDetectorRef.detectChanges();
        });
    };
    AppComponent.prototype.initiliseScriptedForms = function (options) {
        this.myInitialisationService.initiliseScriptedForms(options);
    };
    AppComponent.prototype.initiliseBaseScriptedForms = function (options) {
        this.myInitialisationService.initiliseBaseScriptedForms(options);
    };
    AppComponent.prototype.setTemplateToString = function (dummyPath, template) {
        this.myFileService.setTemplateToString(dummyPath, template);
    };
    __decorate([
        core_1.ViewChild('formBuilderComponent'),
        __metadata("design:type", form_builder_component_1.FormBuilderComponent)
    ], AppComponent.prototype, "formBuilderComponent", void 0);
    __decorate([
        core_1.ViewChild('jupyterErrorMsg'),
        __metadata("design:type", core_1.ElementRef)
    ], AppComponent.prototype, "jupyterErrorMsg", void 0);
    AppComponent = __decorate([
        core_1.Component({
            selector: 'app-root',
            template: linterWorkaroundHtmlTemplate
        }),
        __metadata("design:paramtypes", [file_service_1.FileService,
            form_service_1.FormService,
            initialisation_service_1.InitialisationService,
            kernel_service_1.KernelService,
            variable_service_1.VariableService,
            core_1.ChangeDetectorRef])
    ], AppComponent);
    return AppComponent;
}());
exports.AppComponent = AppComponent;
//# sourceMappingURL=app.component.js.map