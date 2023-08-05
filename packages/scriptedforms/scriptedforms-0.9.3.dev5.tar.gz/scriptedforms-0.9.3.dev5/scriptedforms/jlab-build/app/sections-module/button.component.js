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
/*
Creates the [button] section.

A section that runs all code within it whenever the user presses the provided
button.

By calling the function `runCode` on this component all code components within
this section will be iteratively run. The button is set to call the runCode
function on click.
*/
var core_1 = require("@angular/core");
var section_base_component_1 = require("./section-base.component");
var conditional_component_1 = require("../variables-module/conditional.component");
var ButtonComponent = /** @class */ (function (_super) {
    __extends(ButtonComponent, _super);
    function ButtonComponent(myElementRef) {
        var _this = _super.call(this) || this;
        _this.myElementRef = myElementRef;
        _this.sectionType = 'button';
        _this.inline = null;
        _this.conditionalValue = true;
        return _this;
    }
    Object.defineProperty(ButtonComponent.prototype, "name", {
        set: function (nameInput) {
            this.value = nameInput;
            var element = this.myElementRef.nativeElement;
            var divElement = document.createElement('div');
            divElement.innerHTML = "\n<pre>\n<span class=\"ansi-red-fg\">\n  The use of the \"name\" parameter has been deprecated. Please use the\n  \"value\" parameter instead.\n\n  Replace:\n\n      &lt;section-button name=\"" + this.value + "\"&gt;\n\n  With:\n\n      &lt;section-button value=\"" + this.value + "\"&gt;\n</span>\n</pre>\n    ";
            divElement.classList.add('jp-RenderedText');
            element.appendChild(divElement);
        },
        enumerable: true,
        configurable: true
    });
    ButtonComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        _super.prototype.ngAfterViewInit.call(this);
        if (this.conditional) {
            var value = this.conditionalComponent.variableValue;
            this.conditionalValue = value;
            this.conditionalComponent.variableChange.asObservable().subscribe(function (newValue) {
                _this.conditionalValue = newValue;
            });
        }
    };
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], ButtonComponent.prototype, "inline", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], ButtonComponent.prototype, "conditional", void 0);
    __decorate([
        core_1.ViewChild('conditionalComponent'),
        __metadata("design:type", conditional_component_1.ConditionalComponent)
    ], ButtonComponent.prototype, "conditionalComponent", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], ButtonComponent.prototype, "value", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String),
        __metadata("design:paramtypes", [String])
    ], ButtonComponent.prototype, "name", null);
    ButtonComponent = __decorate([
        core_1.Component({
            selector: 'section-button',
            template: "<div style=\"min-height: 36px;\">\n  <div [class.float-right]=\"inline === null\">\n    <variable-conditional #conditionalComponent *ngIf=\"conditional\">{{conditional}}</variable-conditional>\n    <button *ngIf=\"value\"\n      mat-raised-button color=\"accent\"\n      (click)=\"runCode()\"\n      [disabled]=\"!isFormReady || codeRunning || !conditionalValue\">\n      {{value}}\n    </button>\n    <button *ngIf=\"!value\"\n      mat-mini-fab\n      (click)=\"runCode()\"\n      [disabled]=\"!isFormReady || codeRunning || !conditionalValue\">\n      <mat-icon>keyboard_return</mat-icon>\n    </button>\n  </div>\n  <ng-content></ng-content>\n  <div><code *ngIf=\"code\" class=\"language-python\">{{code}}</code></div>\n</div>\n"
        }),
        __metadata("design:paramtypes", [core_1.ElementRef])
    ], ButtonComponent);
    return ButtonComponent;
}(section_base_component_1.SectionBaseComponent));
exports.ButtonComponent = ButtonComponent;
//# sourceMappingURL=button.component.js.map