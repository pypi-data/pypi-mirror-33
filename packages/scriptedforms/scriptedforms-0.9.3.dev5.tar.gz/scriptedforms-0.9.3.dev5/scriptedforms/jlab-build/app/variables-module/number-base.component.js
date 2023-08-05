"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
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
var core_1 = require("@angular/core");
var variable_base_component_1 = require("./variable-base.component");
var NumberBaseComponent = /** @class */ (function (_super) {
    __extends(NumberBaseComponent, _super);
    function NumberBaseComponent() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.min = null;
        _this.max = null;
        _this.step = 1;
        _this.usedSeparator = false;
        return _this;
    }
    // variableValue: number
    NumberBaseComponent.prototype.loadVariableName = function () {
        var element = this.variablecontainer.nativeElement;
        var ngContent = this.htmlDecode(element.innerHTML).trim();
        // Make both , and ; work for now, remove this in version 0.8.0.
        var items = ngContent.split(/[,;]/);
        if (items.length > 1) {
            this.usedSeparator = true;
        }
        this.variableName = items[0].trim();
        if (items.length > 1) {
            this.min = Number(items[1]);
        }
        if (items.length > 2) {
            this.max = Number(items[2]);
        }
        if (items.length > 3) {
            this.step = Number(items[3]);
        }
    };
    __decorate([
        core_1.Input(),
        __metadata("design:type", Number)
    ], NumberBaseComponent.prototype, "min", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", Number)
    ], NumberBaseComponent.prototype, "max", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", Object)
    ], NumberBaseComponent.prototype, "step", void 0);
    NumberBaseComponent = __decorate([
        core_1.Component({
            template: ''
        })
    ], NumberBaseComponent);
    return NumberBaseComponent;
}(variable_base_component_1.VariableBaseComponent));
exports.NumberBaseComponent = NumberBaseComponent;
//# sourceMappingURL=number-base.component.js.map