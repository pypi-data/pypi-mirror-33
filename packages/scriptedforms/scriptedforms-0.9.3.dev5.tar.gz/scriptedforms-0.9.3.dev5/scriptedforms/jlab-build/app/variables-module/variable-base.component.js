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
/*
Component that handles both [string] and [number] inputs.

In the future these should be more intelligently split out. Potentially create
a base class from which the two types of inputs inherit.

The VariableComponent calls Python code to derive its value initially. Each
time the value is changed it then recalls Python code to update the value.
*/
var core_1 = require("@angular/core");
var variable_service_1 = require("../services/variable.service");
var VariableBaseComponent = /** @class */ (function () {
    function VariableBaseComponent(myChangeDetectorRef, myVariableService, myElementRef) {
        this.myChangeDetectorRef = myChangeDetectorRef;
        this.myVariableService = myVariableService;
        this.myElementRef = myElementRef;
        this.isOutput = false;
        this.isFormReady = false;
        this.isPandas = false;
        this.isFocus = false;
        this.variableChange = new core_1.EventEmitter();
        this.oldVariableValue = null;
        this.variableValue = null;
        this.placeholder = '';
    }
    VariableBaseComponent.prototype.htmlDecode = function (input) {
        var e = document.createElement('div');
        e.innerHTML = input;
        var result = e.childNodes[0].nodeValue;
        e.remove();
        return result;
    };
    VariableBaseComponent.prototype.loadVariableName = function () {
        var element = this.variablecontainer.nativeElement;
        this.variableName = this.htmlDecode(element.innerHTML).trim();
    };
    VariableBaseComponent.prototype.ngAfterViewInit = function () {
        this.loadVariableName();
        if (this.name) {
            this.label = this.name;
            var element = this.myElementRef.nativeElement;
            var divElement = document.createElement('div');
            divElement.innerHTML = "\n<pre>\n  <span class=\"ansi-red-fg\">\n    The use of the \"name\" parameter has been deprecated. Please use the\n    \"label\" parameter instead.\n\n    Replace:\n\n        &lt;variable-* name=\"" + this.name + "\"&gt;" + this.variableName + "&lt;/variable-*&gt;\n\n    With:\n\n        &lt;variable-* label=\"" + this.name + "\"&gt;" + this.variableName + "&lt;/variable-*&gt;\n  </span>\n</pre>\n      ";
            divElement.classList.add('jp-RenderedText');
            element.appendChild(divElement);
        }
        if (this.label) {
            this.labelValue = this.label;
        }
        else {
            this.labelValue = this.variableName;
        }
        this.myChangeDetectorRef.detectChanges();
    };
    VariableBaseComponent.prototype.onBlur = function (tableCoords) {
        this.isFocus = false;
    };
    VariableBaseComponent.prototype.onFocus = function (tableCoords) {
        this.isFocus = true;
    };
    VariableBaseComponent.prototype.pythonValueReference = function () {
        return "json.loads(r'" + JSON.stringify(this.variableValue) + "')";
    };
    VariableBaseComponent.prototype.pythonVariableEvaluate = function () {
        return "" + this.variableName;
    };
    VariableBaseComponent.prototype.testIfDifferent = function () {
        return this.variableValue !== this.oldVariableValue;
    };
    VariableBaseComponent.prototype.updateOldVariable = function () {
        this.oldVariableValue = JSON.parse(JSON.stringify(this.variableValue));
    };
    VariableBaseComponent.prototype.variableChanged = function () {
        var _this = this;
        if (this.testIfDifferent()) {
            var valueReference = this.pythonValueReference();
            this.myVariableService.pushVariable(this.variableIdentifier, this.variableName, valueReference)
                .then(function (status) {
                if (status !== 'ignore') {
                    _this.variableChange.emit(_this.variableValue);
                }
            });
            this.updateOldVariable();
        }
    };
    VariableBaseComponent.prototype.updateVariableView = function (value) {
        if (!this.isFocus) {
            if (this.variableValue !== value) {
                this.variableValue = value;
                this.updateOldVariable();
                this.variableChange.emit(this.variableValue);
            }
        }
    };
    VariableBaseComponent.prototype.formReady = function (isReady) {
        this.isFormReady = isReady;
    };
    VariableBaseComponent.prototype.setId = function (index) {
        this.variableIdentifier = "(" + String(index) + ")-" + this.variableName;
    };
    VariableBaseComponent.prototype.initialise = function () {
        this.myVariableService.initialiseVariableComponent(this);
    };
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], VariableBaseComponent.prototype, "required", void 0);
    __decorate([
        core_1.Output(),
        __metadata("design:type", Object)
    ], VariableBaseComponent.prototype, "variableChange", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], VariableBaseComponent.prototype, "name", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], VariableBaseComponent.prototype, "label", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", Object)
    ], VariableBaseComponent.prototype, "placeholder", void 0);
    __decorate([
        core_1.ViewChild('variablecontainer'),
        __metadata("design:type", core_1.ElementRef)
    ], VariableBaseComponent.prototype, "variablecontainer", void 0);
    VariableBaseComponent = __decorate([
        core_1.Component({
            template: ''
        }),
        __metadata("design:paramtypes", [core_1.ChangeDetectorRef,
            variable_service_1.VariableService,
            core_1.ElementRef])
    ], VariableBaseComponent);
    return VariableBaseComponent;
}());
exports.VariableBaseComponent = VariableBaseComponent;
//# sourceMappingURL=variable-base.component.js.map