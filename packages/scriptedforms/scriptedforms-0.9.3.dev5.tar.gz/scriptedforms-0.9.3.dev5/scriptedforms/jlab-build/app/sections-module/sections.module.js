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
var material_1 = require("@angular/material");
var code_module_1 = require("../code-module/code.module");
var section_base_component_1 = require("./section-base.component");
var start_component_1 = require("./start.component");
var live_component_1 = require("./live.component");
var button_component_1 = require("./button.component");
var output_component_1 = require("./output.component");
var section_file_change_component_1 = require("./section-file-change.component");
var variables_module_1 = require("../variables-module/variables.module");
var SectionsModule = /** @class */ (function () {
    function SectionsModule() {
    }
    SectionsModule = __decorate([
        core_1.NgModule({
            imports: [
                common_1.CommonModule,
                material_1.MatButtonModule,
                material_1.MatIconModule,
                variables_module_1.VariablesModule,
                code_module_1.CodeModule
            ],
            declarations: [
                section_base_component_1.SectionBaseComponent,
                start_component_1.StartComponent,
                live_component_1.LiveComponent,
                button_component_1.ButtonComponent,
                output_component_1.OutputComponent,
                section_file_change_component_1.SectionFileChangeComponent
            ],
            exports: [
                start_component_1.StartComponent,
                live_component_1.LiveComponent,
                button_component_1.ButtonComponent,
                output_component_1.OutputComponent,
                section_file_change_component_1.SectionFileChangeComponent
            ]
        })
    ], SectionsModule);
    return SectionsModule;
}());
exports.SectionsModule = SectionsModule;
//# sourceMappingURL=sections.module.js.map