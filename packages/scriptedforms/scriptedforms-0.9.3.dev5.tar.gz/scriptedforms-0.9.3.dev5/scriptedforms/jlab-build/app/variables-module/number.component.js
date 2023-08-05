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
var number_base_component_1 = require("./number-base.component");
var core_1 = require("@angular/core");
var NumberComponent = /** @class */ (function (_super) {
    __extends(NumberComponent, _super);
    function NumberComponent() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    NumberComponent = __decorate([
        core_1.Component({
            selector: 'variable-number',
            template: "\n<span #variablecontainer *ngIf=\"variableName === undefined\">\n  <ng-content></ng-content>\n</span>\n\n<mat-form-field class=\"variableNumber\" *ngIf=\"variableName\" >\n  <mat-label>{{labelValue}}</mat-label>\n  <input\n  [required]=\"required\"\n  matInput\n  [disabled]=\"!isFormReady\"\n  [placeholder]=\"placeholder\"\n  [(ngModel)]=\"variableValue\"\n  (ngModelChange)=\"variableChanged($event)\"\n  (blur)=\"onBlur()\"\n  (focus)=\"onFocus()\"\n  [max]=\"max\"\n  [min]=\"min\"\n  [step]=\"step\"\n  type=\"number\">\n</mat-form-field>\n<div class=\"jp-RenderedText\" *ngIf=\"usedSeparator\">\n  <pre>\n    <span class=\"ansi-red-fg\">\n      The use of commas or semicolons to separate inputs is deprecated.\n      Please instead use html parameters like so:\n      &lt;variable-number min=\"{{min}}\" max=\"{{max}}\" step=\"{{step}}\"&gt;{{variableName}}&lt;/variable-number&gt;\n    </span>\n  </pre>\n</div>",
            styles: [
                ".variableNumber {\n    width: 200px;\n  }\n  "
            ]
        })
    ], NumberComponent);
    return NumberComponent;
}(number_base_component_1.NumberBaseComponent));
exports.NumberComponent = NumberComponent;
//# sourceMappingURL=number.component.js.map