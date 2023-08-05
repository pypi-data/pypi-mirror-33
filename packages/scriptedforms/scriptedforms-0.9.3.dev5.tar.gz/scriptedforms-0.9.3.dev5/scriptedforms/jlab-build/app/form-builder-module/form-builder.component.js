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
The Form Component has a function `setFormContents` which is callable on this
component with a string input. Once this function is called the form rebuilds
with the provided contents.
*/
var core_1 = require("@angular/core");
var coreutils_1 = require("@phosphor/coreutils");
var MarkdownIt = require("markdown-it");
var file_service_1 = require("../services/file.service");
var create_form_component_factory_1 = require("./create-form-component-factory");
var FormBuilderComponent = /** @class */ (function () {
    function FormBuilderComponent(compiler, 
        // private myFormService: FormService,
        // private myWatchdogService: WatchdogService,
        myFileService) {
        this.compiler = compiler;
        this.myFileService = myFileService;
        this.viewInitialised = new coreutils_1.PromiseDelegate();
    }
    FormBuilderComponent.prototype.ngOnInit = function () {
        this.myMarkdownIt = new MarkdownIt({
            html: true,
            linkify: true,
            typographer: true
        });
    };
    FormBuilderComponent.prototype.ngAfterViewInit = function () {
        this.errorboxDiv = this.errorbox.nativeElement;
        this.viewInitialised.resolve(null);
    };
    // https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest
    FormBuilderComponent.prototype._setUsageStatistics = function (string) {
        var _this = this;
        if (string) {
            crypto.subtle.digest('SHA-256', Buffer.from(string)).then(function (hash) {
                var intArrayHash = new Uint8Array(hash);
                var base64String = btoa(String.fromCharCode.apply(null, intArrayHash));
                var uriEncoded = encodeURIComponent(base64String);
                _this.telemetry.nativeElement.src = "https://scriptedforms.com.au/telemetry?hash=" + uriEncoded;
            });
        }
    };
    /**
     * Set or update the template of the form.
     *
     * This function makes sure to only begin building the form once the component
     * has sufficiently initialised.
     */
    FormBuilderComponent.prototype.buildForm = function (markdownTemplate) {
        var _this = this;
        this._setUsageStatistics(markdownTemplate);
        return this.viewInitialised.promise.then(function () {
            var convertedTemplate = _this.convertTemplate(markdownTemplate);
            var htmlTemplate = convertedTemplate['htmlTemplate'];
            var cssStyles = convertedTemplate['cssStyles'];
            // Create the form component
            var formComponent = _this.createFormFromTemplate(htmlTemplate, cssStyles);
            return formComponent.formViewInitialised.promise.then(function () {
                _this.myFileService.renderComplete.resolve(null);
                return formComponent;
            });
        });
    };
    FormBuilderComponent.prototype.stripStyleTags = function (html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var cssStyleNodes = Array.from(tmp.getElementsByTagName('style'));
        var cssStyles = [];
        cssStyleNodes.forEach(function (node) {
            cssStyles = cssStyles.concat([node.innerHTML]);
        });
        tmp.remove();
        return cssStyles;
    };
    /**
     * Convert the form template from markdown to its final html state.
     *
     * @param markdownTemplate The markdown template.
     *
     * @returns The html template.
     */
    FormBuilderComponent.prototype.convertTemplate = function (markdownTemplate) {
        // Add new lines around the sections
        var addNewLines = markdownTemplate
            .replace(/<\/?section-.+>/g, function (match) { return '\n' + match + '\n'; });
        // Render the markdown to html
        var html = this.myMarkdownIt.render(addNewLines);
        var cssStyles = this.stripStyleTags(html);
        var userStyle = document.getElementById('scripted-forms-custom-user-style');
        userStyle.innerHTML = cssStyles.join('\n\n');
        // Escape '{}' characters as these are special characters within Angular
        var escapedHtml = html.replace(/{/g, '@~lb~@').replace(/}/g, '@~rb~@').replace(/@~lb~@/g, '{{ \'{\' }}').replace(/@~rb~@/g, '{{ \'}\' }}');
        var htmlTemplate = escapedHtml;
        var result = {
            htmlTemplate: htmlTemplate, cssStyles: cssStyles
        };
        return result;
    };
    /**
     * Create the form component from the html template with the Angular compiler.
     *
     * @param template The html Angular component template
     */
    FormBuilderComponent.prototype.createFormFromTemplate = function (template, cssStyles) {
        var metadata = {
            selector: "app-form",
            template: template,
            styles: cssStyles
        };
        // Create the form component factory
        var formFactory = create_form_component_factory_1.createFormComponentFactory(this.compiler, metadata);
        // If a form already exists remove it before continuing
        if (this.formComponentRef) {
            this.formComponentRef.destroy();
        }
        // If a previous compile produced an error, clear the error message
        this.errorboxDiv.innerHTML = '';
        // Create the form component
        this.formComponentRef = this.container.createComponent(formFactory);
        if (typeof MathJax !== 'undefined') {
            this.formComponentRef.instance.formReady.promise.then(function () {
                MathJax.Hub.Queue(['Typeset', MathJax.Hub]);
            });
        }
        return this.formComponentRef.instance;
    };
    __decorate([
        core_1.ViewChild('errorbox'),
        __metadata("design:type", core_1.ElementRef)
    ], FormBuilderComponent.prototype, "errorbox", void 0);
    __decorate([
        core_1.ViewChild('telemetry'),
        __metadata("design:type", core_1.ElementRef)
    ], FormBuilderComponent.prototype, "telemetry", void 0);
    __decorate([
        core_1.ViewChild('container', { read: core_1.ViewContainerRef }),
        __metadata("design:type", core_1.ViewContainerRef)
    ], FormBuilderComponent.prototype, "container", void 0);
    FormBuilderComponent = __decorate([
        core_1.Component({
            selector: 'app-form-builder',
            template: "\n<div class=\"form-contents\"><ng-content></ng-content>\n  <div #errorbox class=\"errorbox\"></div>\n  <div #container></div>\n</div>\n<iframe #telemetry class=\"hidden-iframe\"></iframe>\n"
        }),
        __metadata("design:paramtypes", [core_1.Compiler,
            file_service_1.FileService])
    ], FormBuilderComponent);
    return FormBuilderComponent;
}());
exports.FormBuilderComponent = FormBuilderComponent;
//# sourceMappingURL=form-builder.component.js.map