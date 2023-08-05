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
var core_1 = require("@angular/core");
var section_base_component_1 = require("./section-base.component");
var variable_service_1 = require("../services/variable.service");
var OutputComponent = /** @class */ (function (_super) {
    __extends(OutputComponent, _super);
    function OutputComponent(myVariableService) {
        var _this = _super.call(this) || this;
        _this.myVariableService = myVariableService;
        _this.sectionType = 'output';
        _this.hasFirstSubRun = false;
        return _this;
    }
    OutputComponent.prototype.subscribeToVariableChanges = function () {
        var _this = this;
        this.variableSubscription = this.myVariableService.variableChangedObservable
            .subscribe(function (value) {
            if (_this.hasFirstSubRun) {
                if (value !== null) {
                    _this.runCode();
                }
            }
            else {
                _this.hasFirstSubRun = true;
            }
        });
    };
    OutputComponent.prototype.unsubscribe = function () {
        this.variableSubscription.unsubscribe();
    };
    OutputComponent.prototype.kernelReset = function () {
        this.unsubscribe();
    };
    OutputComponent.prototype.ngOnDestroy = function () {
        this.unsubscribe();
    };
    OutputComponent = __decorate([
        core_1.Component({
            selector: 'section-output',
            template: "<ng-content></ng-content><div><code *ngIf=\"code\" class=\"language-python\">{{code}}</code></div>"
        }),
        __metadata("design:paramtypes", [variable_service_1.VariableService])
    ], OutputComponent);
    return OutputComponent;
}(section_base_component_1.SectionBaseComponent));
exports.OutputComponent = OutputComponent;
//# sourceMappingURL=output.component.js.map