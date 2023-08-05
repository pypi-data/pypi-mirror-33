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
var variable_parameter_component_1 = require("../variables-module/variable-parameter.component");
var watchdog_service_1 = require("../services/watchdog.service");
var SectionFileChangeComponent = /** @class */ (function (_super) {
    __extends(SectionFileChangeComponent, _super);
    function SectionFileChangeComponent(myWatchdogService) {
        var _this = _super.call(this) || this;
        _this.myWatchdogService = myWatchdogService;
        _this.sectionType = 'filechange';
        return _this;
    }
    SectionFileChangeComponent.prototype.updateFilepathObserver = function () {
        var _this = this;
        this.pathsConverted.forEach(function (value) {
            _this.myWatchdogService.addFilepathObserver(value);
        });
    };
    SectionFileChangeComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        _super.prototype.ngAfterViewInit.call(this);
        // this.updateFilepathObserver()
        this.variableParameterComponent.variableChange.asObservable().subscribe(function (value) {
            _this.pathsConverted = value;
            _this.updateFilepathObserver();
        });
        this.watchdogSubscription = this.myWatchdogService.fileChanged.subscribe(function (value) {
            if (_this.pathsConverted) {
                if ((_this.pathsConverted.includes(value)) ||
                    (_this.pathsConverted.includes("./" + value)) ||
                    (_this.pathsConverted.includes(".\\" + value))) {
                    _this.runCode();
                }
            }
        });
    };
    SectionFileChangeComponent.prototype.ngOnDestroy = function () {
        this.watchdogSubscription.unsubscribe();
    };
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], SectionFileChangeComponent.prototype, "paths", void 0);
    __decorate([
        core_1.ViewChild('variableParameterComponent'),
        __metadata("design:type", variable_parameter_component_1.VariableParameterComponent)
    ], SectionFileChangeComponent.prototype, "variableParameterComponent", void 0);
    SectionFileChangeComponent = __decorate([
        core_1.Component({
            selector: 'section-filechange',
            template: "<variable-parameter #variableParameterComponent *ngIf='paths'>\n_watchdog_path_conversion({{paths}})\n</variable-parameter><ng-content></ng-content><code *ngIf=\"code\" class=\"language-python\">{{code}}</code>"
        }),
        __metadata("design:paramtypes", [watchdog_service_1.WatchdogService])
    ], SectionFileChangeComponent);
    return SectionFileChangeComponent;
}(section_base_component_1.SectionBaseComponent));
exports.SectionFileChangeComponent = SectionFileChangeComponent;
//# sourceMappingURL=section-file-change.component.js.map