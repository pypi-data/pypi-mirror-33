"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
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
/*
The root app module.
*/
var platform_browser_1 = require("@angular/platform-browser");
var core_1 = require("@angular/core");
var forms_1 = require("@angular/forms");
var animations_1 = require("@angular/platform-browser/animations");
var material_module_1 = require("../vendors/material.module");
var app_error_handler_1 = require("./app-error-handler");
var kernel_service_1 = require("./services/kernel.service");
var variable_service_1 = require("./services/variable.service");
var file_service_1 = require("./services/file.service");
var watchdog_service_1 = require("./services/watchdog.service");
var form_service_1 = require("./services/form.service");
var jupyter_service_1 = require("./services/jupyter.service");
var initialisation_service_1 = require("./services/initialisation.service");
var toolbar_service_1 = require("./services/toolbar.service");
var form_builder_module_1 = require("./form-builder-module/form-builder.module");
var toolbar_module_1 = require("./toolbar-module/toolbar.module");
var toolbar_button_component_1 = require("./toolbar-module/toolbar-button.component");
var app_component_1 = require("./app.component");
var AppModule = /** @class */ (function () {
    function AppModule() {
    }
    AppModule.prototype.ngDoBootstrap = function (app) { };
    AppModule = __decorate([
        core_1.NgModule({
            declarations: [
                app_component_1.AppComponent
            ],
            imports: [
                animations_1.BrowserAnimationsModule,
                platform_browser_1.BrowserModule,
                forms_1.FormsModule,
                material_module_1.MaterialModule,
                form_builder_module_1.FormBuilderModule,
                toolbar_module_1.ToolbarModule
            ],
            entryComponents: [app_component_1.AppComponent, toolbar_button_component_1.ToolbarButtonComponent],
            providers: [
                kernel_service_1.KernelService,
                variable_service_1.VariableService,
                file_service_1.FileService,
                watchdog_service_1.WatchdogService,
                form_service_1.FormService,
                jupyter_service_1.JupyterService,
                initialisation_service_1.InitialisationService,
                toolbar_service_1.ToolbarService,
                { provide: core_1.ErrorHandler, useClass: app_error_handler_1.AppErrorHandler }
            ],
            exports: [
                app_component_1.AppComponent,
            ]
        })
    ], AppModule);
    return AppModule;
}());
exports.AppModule = AppModule;
//# sourceMappingURL=app.module.js.map