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
Creates the [button] section.

A section that runs all code within it whenever the user presses the provided
button.

By calling the function `runCode` on this component all code components within
this section will be iteratively run. The button is set to call the runCode
function on click.
*/
var rxjs_1 = require("rxjs");
var core_1 = require("@angular/core");
var core_2 = require("@angular/core");
var widgets_1 = require("@phosphor/widgets");
var toolbar_button_component_1 = require("./toolbar-button.component");
var toolbar_service_1 = require("../services/toolbar.service");
var form_service_1 = require("../services/form.service");
var ToolbarBaseComponent = /** @class */ (function () {
    function ToolbarBaseComponent(myComponentFactoryResolver, myToolbarService, myFormService, changeDetectorRef) {
        this.myComponentFactoryResolver = myComponentFactoryResolver;
        this.myToolbarService = myToolbarService;
        this.myFormService = myFormService;
        this.changeDetectorRef = changeDetectorRef;
        this.restartingKernel = new rxjs_1.BehaviorSubject(false);
    }
    ToolbarBaseComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        this.addButton({
            icon: 'chrome_reader_mode',
            // href: '../docs',  // Only change this link once the docs are ready
            href: 'https://scriptedforms.com.au',
            tooltip: 'ScriptedForms documentation, installation instructions, and source code.'
        });
        this.addButton({
            click: function () { window.print(); },
            icon: 'print',
            tooltip: 'Print your ScriptedForm'
        });
        this.addButton({
            click: function () { _this.restartKernel(); },
            icon: 'refresh',
            disable: this.restartingKernel,
            tooltip: 'Restart the Jupyter Python Kernel. This will reset your inputs.'
        });
        this.myToolbarService.addSpacer();
        this.changeDetectorRef.detectChanges();
    };
    ToolbarBaseComponent.prototype.addButton = function (options) {
        this.buttonFactory = this.myComponentFactoryResolver.resolveComponentFactory(toolbar_button_component_1.ToolbarButtonComponent);
        var button = this.container.createComponent(this.buttonFactory);
        button.instance.options = options;
        var widget = new widgets_1.Widget({ node: button.instance.myElementRef.nativeElement });
        this.myToolbarService.addItem(options.icon, widget);
    };
    ToolbarBaseComponent.prototype.restartKernel = function () {
        var _this = this;
        this.restartingKernel.next(true);
        this.myFormService.restartFormKernel().then(function () {
            _this.restartingKernel.next(false);
        });
    };
    __decorate([
        core_1.ViewChild('container', { read: core_1.ViewContainerRef }),
        __metadata("design:type", core_1.ViewContainerRef)
    ], ToolbarBaseComponent.prototype, "container", void 0);
    ToolbarBaseComponent = __decorate([
        core_2.Component({
            selector: 'toolbar-base',
            template: "<span #container></span><toolbar-button hidden></toolbar-button>"
        }),
        __metadata("design:paramtypes", [core_1.ComponentFactoryResolver,
            toolbar_service_1.ToolbarService,
            form_service_1.FormService,
            core_1.ChangeDetectorRef])
    ], ToolbarBaseComponent);
    return ToolbarBaseComponent;
}());
exports.ToolbarBaseComponent = ToolbarBaseComponent;
//# sourceMappingURL=toolbar-base.component.js.map