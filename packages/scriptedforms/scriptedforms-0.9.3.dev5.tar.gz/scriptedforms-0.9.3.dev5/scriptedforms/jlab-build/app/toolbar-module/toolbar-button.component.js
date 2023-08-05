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
var core_1 = require("@angular/core");
var ToolbarButtonComponent = /** @class */ (function () {
    function ToolbarButtonComponent(myElementRef) {
        this.myElementRef = myElementRef;
        this.previousSubscription = null;
        this.isDisabled = false;
    }
    Object.defineProperty(ToolbarButtonComponent.prototype, "options", {
        set: function (optionsInput) {
            var _this = this;
            this._options = optionsInput;
            if (optionsInput.disable) {
                if (this.previousSubscription) {
                    this.previousSubscription.unsubscribe();
                }
                this.previousSubscription = optionsInput.disable.subscribe(function (disableInput) {
                    _this.isDisabled = disableInput;
                });
            }
        },
        enumerable: true,
        configurable: true
    });
    __decorate([
        core_1.Input(),
        __metadata("design:type", Object),
        __metadata("design:paramtypes", [Object])
    ], ToolbarButtonComponent.prototype, "options", null);
    __decorate([
        core_1.ViewChild('button'),
        __metadata("design:type", core_1.ElementRef)
    ], ToolbarButtonComponent.prototype, "button", void 0);
    ToolbarButtonComponent = __decorate([
        core_1.Component({
            selector: 'toolbar-button',
            template: "<span *ngIf=\"_options\">\n<a *ngIf=\"_options.href\" #button\n  [href]=\"_options.href\"\n  [disabled]=\"isDisabled\"\n  [title]=\"_options.tooltip\"\n  mat-icon-button>\n    <mat-icon>{{_options.icon}}</mat-icon>\n</a>\n<button *ngIf=\"_options.click\" #button\n  (click)=\"_options.click()\"\n  [disabled]=\"isDisabled\"\n  [title]=\"_options.tooltip\"\n  mat-icon-button>\n    <mat-icon>{{_options.icon}}</mat-icon>\n</button>\n</span>\n\n"
        }),
        __metadata("design:paramtypes", [core_1.ElementRef])
    ], ToolbarButtonComponent);
    return ToolbarButtonComponent;
}());
exports.ToolbarButtonComponent = ToolbarButtonComponent;
//# sourceMappingURL=toolbar-button.component.js.map