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
var number_base_component_1 = require("./number-base.component");
// import { Slider } from '../interfaces/slider';
// import * as  stringify from 'json-stable-stringify';
var SliderComponent = /** @class */ (function (_super) {
    __extends(SliderComponent, _super);
    function SliderComponent() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.min = 0;
        _this.max = 100;
        return _this;
    }
    SliderComponent.prototype.updateValue = function (value) {
        this.variableValue = value;
        this.variableChanged();
    };
    __decorate([
        core_1.Input(),
        __metadata("design:type", Object)
    ], SliderComponent.prototype, "min", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", Object)
    ], SliderComponent.prototype, "max", void 0);
    SliderComponent = __decorate([
        core_1.Component({
            selector: 'variable-slider',
            template: "\n<span #variablecontainer *ngIf=\"variableName === undefined\">\n  <ng-content></ng-content>\n</span>\n\n<span class=\"container\">{{labelValue}}\n  <mat-slider class=\"variableSlider\" *ngIf=\"variableName\"\n  [disabled]=\"!isFormReady\"\n  [value]=\"variableValue\"\n  (input)=\"updateValue($event.value)\"\n  (blur)=\"onBlur()\"\n  (focus)=\"onFocus()\"\n  [max]=\"max\"\n  [min]=\"min\"\n  [step]=\"step\"\n  [thumbLabel]=\"true\">\n  </mat-slider>\n</span>\n<div class=\"jp-RenderedText\" *ngIf=\"usedSeparator\">\n  <pre>\n  <span class=\"ansi-red-fg\">\n  The use of commas or semicolons to separate inputs is deprecated.\n  Please instead use html parameters like so:\n  &lt;variable-slider min=\"{{min}}\" max=\"{{max}}\" step=\"{{step}}\"&gt;{{variableName}}&lt;/variable-slider&gt;\n</span>\n  </pre>\n</div>",
            styles: [
                "\n.container {\n  display: flex;\n}\n\n.variableSlider {\n  flex-grow: 1;\n}\n"
            ]
        })
    ], SliderComponent);
    return SliderComponent;
}(number_base_component_1.NumberBaseComponent));
exports.SliderComponent = SliderComponent;
//# sourceMappingURL=slider.component.js.map