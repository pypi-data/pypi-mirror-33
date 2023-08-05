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
A module containing the form elements.
*/
var core_1 = require("@angular/core");
var common_1 = require("@angular/common");
var forms_1 = require("@angular/forms");
var material_module_1 = require("../../vendors/material.module");
var variable_base_component_1 = require("./variable-base.component");
var number_base_component_1 = require("./number-base.component");
var toggle_component_1 = require("./toggle.component");
var tick_component_1 = require("./tick.component");
var conditional_component_1 = require("./conditional.component");
var number_component_1 = require("./number.component");
var slider_component_1 = require("./slider.component");
var variable_table_component_1 = require("./variable-table.component");
var string_component_1 = require("./string.component");
var dropdown_component_1 = require("./dropdown.component");
var variable_parameter_component_1 = require("./variable-parameter.component");
var variable_file_component_1 = require("./variable-file.component");
var VariablesModule = /** @class */ (function () {
    function VariablesModule() {
    }
    VariablesModule = __decorate([
        core_1.NgModule({
            imports: [
                common_1.CommonModule,
                material_module_1.MaterialModule,
                forms_1.FormsModule
            ],
            declarations: [
                variable_base_component_1.VariableBaseComponent,
                number_base_component_1.NumberBaseComponent,
                toggle_component_1.ToggleComponent,
                tick_component_1.TickComponent,
                conditional_component_1.ConditionalComponent,
                number_component_1.NumberComponent,
                slider_component_1.SliderComponent,
                variable_table_component_1.VariableTableComponent,
                string_component_1.StringComponent,
                dropdown_component_1.DropdownComponent,
                variable_parameter_component_1.VariableParameterComponent,
                variable_file_component_1.VariableFileComponent
            ],
            exports: [
                toggle_component_1.ToggleComponent,
                tick_component_1.TickComponent,
                conditional_component_1.ConditionalComponent,
                number_component_1.NumberComponent,
                slider_component_1.SliderComponent,
                variable_table_component_1.VariableTableComponent,
                string_component_1.StringComponent,
                dropdown_component_1.DropdownComponent,
                variable_parameter_component_1.VariableParameterComponent,
                variable_file_component_1.VariableFileComponent
            ]
        })
    ], VariablesModule);
    return VariablesModule;
}());
exports.VariablesModule = VariablesModule;
//# sourceMappingURL=variables.module.js.map