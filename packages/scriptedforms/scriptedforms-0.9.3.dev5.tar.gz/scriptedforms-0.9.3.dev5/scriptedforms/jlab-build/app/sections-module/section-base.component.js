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
var core_1 = require("@angular/core");
var coreutils_1 = require("@phosphor/coreutils");
var code_component_1 = require("../code-module/code.component");
var SectionBaseComponent = /** @class */ (function () {
    function SectionBaseComponent() {
        this.isFormReady = false;
        this.codeRunning = false;
        this.formReadyPromiseDelegate = new coreutils_1.PromiseDelegate();
        this.viewInitPromiseDelegate = new coreutils_1.PromiseDelegate();
    }
    SectionBaseComponent.prototype.ngAfterViewInit = function () {
        this.viewInitPromiseDelegate.resolve(null);
        this.codeComponentsArray = this.contentCodeComponents.toArray().concat(this.viewCodeComponents.toArray());
    };
    SectionBaseComponent.prototype.runCode = function (evenIfNotReady) {
        var _this = this;
        if (evenIfNotReady === void 0) { evenIfNotReady = false; }
        if (evenIfNotReady || this.formReady) {
            var runCodeComplete_1 = new coreutils_1.PromiseDelegate();
            this.viewInitPromiseDelegate.promise
                .then(function () {
                _this.codeRunning = true;
                _this._runAllCodeComponents(runCodeComplete_1);
                runCodeComplete_1.promise.then(function () {
                    _this.codeRunning = false;
                });
            });
            return runCodeComplete_1.promise;
        }
        else {
            console.log("did not run, form not ready: \"" + this.sectionType + "\"_" + this.sectionId);
            return Promise.resolve(null);
        }
    };
    SectionBaseComponent.prototype._runAllCodeComponents = function (runCodeComplete) {
        var promiseList = [];
        this.codeComponentsArray.forEach(function (codeComponent, index) {
            promiseList.push(codeComponent.runCode());
        });
        Promise.all(promiseList).then(function () {
            runCodeComplete.resolve(null);
        });
    };
    SectionBaseComponent.prototype.formReady = function (isReady) {
        this.formReadyPromiseDelegate.resolve(null);
        this.isFormReady = isReady;
    };
    SectionBaseComponent.prototype.setId = function (id) {
        var _this = this;
        this.sectionId = id;
        this.codeComponentsArray.forEach(function (codeComponent, index) {
            codeComponent.name = "\"" + _this.sectionType + "\"_" + _this.sectionId + "_" + index;
        });
    };
    SectionBaseComponent.prototype.kernelReset = function () { };
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], SectionBaseComponent.prototype, "onLoad", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], SectionBaseComponent.prototype, "code", void 0);
    __decorate([
        core_1.ContentChildren(code_component_1.CodeComponent),
        __metadata("design:type", core_1.QueryList)
    ], SectionBaseComponent.prototype, "contentCodeComponents", void 0);
    __decorate([
        core_1.ViewChildren(code_component_1.CodeComponent),
        __metadata("design:type", core_1.QueryList)
    ], SectionBaseComponent.prototype, "viewCodeComponents", void 0);
    SectionBaseComponent = __decorate([
        core_1.Component({
            template: ''
        })
    ], SectionBaseComponent);
    return SectionBaseComponent;
}());
exports.SectionBaseComponent = SectionBaseComponent;
//# sourceMappingURL=section-base.component.js.map