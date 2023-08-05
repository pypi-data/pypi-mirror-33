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
var toggle_component_1 = require("../variables-module/toggle.component");
var tick_component_1 = require("../variables-module/tick.component");
var conditional_component_1 = require("../variables-module/conditional.component");
var number_component_1 = require("../variables-module/number.component");
var slider_component_1 = require("../variables-module/slider.component");
var variable_table_component_1 = require("../variables-module/variable-table.component");
var string_component_1 = require("../variables-module/string.component");
var dropdown_component_1 = require("../variables-module/dropdown.component");
var variable_file_component_1 = require("../variables-module/variable-file.component");
var code_component_1 = require("../code-module/code.component");
var LiveComponent = /** @class */ (function (_super) {
    __extends(LiveComponent, _super);
    function LiveComponent() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.sectionType = 'live';
        _this.variableComponents = [];
        // hasFirstSubRun = false;
        _this.subscriptions = [];
        return _this;
    }
    LiveComponent.prototype.ngAfterViewInit = function () {
        _super.prototype.ngAfterViewInit.call(this);
        this.variableComponents = this.variableComponents.concat(this.toggleComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.tickComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.conditionalComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.numberComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.sliderComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.variableTableComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.stringComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.dropdownComponents.toArray());
        this.variableComponents = this.variableComponents.concat(this.variableFileComponents.toArray());
    };
    LiveComponent.prototype.subscribe = function () {
        var _this = this;
        for (var _i = 0, _a = this.variableComponents; _i < _a.length; _i++) {
            var variableComponent = _a[_i];
            this.subscriptions.push(variableComponent.variableChange.asObservable().subscribe(function (value) {
                // if (this.hasFirstSubRun) {
                _this.runCode();
                // } else {
                // this.hasFirstSubRun = true;
                // }
            }));
        }
    };
    LiveComponent.prototype.unsubscribe = function () {
        this.subscriptions.forEach(function (subscription) { return subscription.unsubscribe(); });
    };
    LiveComponent.prototype.kernelReset = function () {
        this.unsubscribe();
    };
    LiveComponent.prototype.ngOnDestroy = function () {
        this.unsubscribe();
    };
    __decorate([
        core_1.ContentChildren(toggle_component_1.ToggleComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "toggleComponents", void 0);
    __decorate([
        core_1.ContentChildren(tick_component_1.TickComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "tickComponents", void 0);
    __decorate([
        core_1.ContentChildren(conditional_component_1.ConditionalComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "conditionalComponents", void 0);
    __decorate([
        core_1.ContentChildren(number_component_1.NumberComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "numberComponents", void 0);
    __decorate([
        core_1.ContentChildren(slider_component_1.SliderComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "sliderComponents", void 0);
    __decorate([
        core_1.ContentChildren(variable_table_component_1.VariableTableComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "variableTableComponents", void 0);
    __decorate([
        core_1.ContentChildren(string_component_1.StringComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "stringComponents", void 0);
    __decorate([
        core_1.ContentChildren(dropdown_component_1.DropdownComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "dropdownComponents", void 0);
    __decorate([
        core_1.ContentChildren(variable_file_component_1.VariableFileComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "variableFileComponents", void 0);
    __decorate([
        core_1.ContentChildren(code_component_1.CodeComponent),
        __metadata("design:type", core_1.QueryList)
    ], LiveComponent.prototype, "codeComponents", void 0);
    LiveComponent = __decorate([
        core_1.Component({
            selector: 'section-live',
            template: "<ng-content></ng-content><div><code *ngIf=\"code\" class=\"language-python\">{{code}}</code></div>"
        })
    ], LiveComponent);
    return LiveComponent;
}(section_base_component_1.SectionBaseComponent));
exports.LiveComponent = LiveComponent;
//# sourceMappingURL=live.component.js.map