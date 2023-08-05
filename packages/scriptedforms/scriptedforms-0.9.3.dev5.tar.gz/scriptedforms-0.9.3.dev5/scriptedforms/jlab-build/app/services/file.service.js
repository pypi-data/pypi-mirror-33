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
var rxjs_1 = require("rxjs");
var coreutils_1 = require("@phosphor/coreutils");
// import * as yaml from 'js-yaml';
var jupyter_service_1 = require("./jupyter.service");
var form_service_1 = require("./form.service");
var kernel_service_1 = require("./kernel.service");
var variable_service_1 = require("./variable.service");
// https://stackoverflow.com/a/6969486/3912576
function escapeRegExp(str) {
    return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, '\\$&');
}
var FileService = /** @class */ (function () {
    function FileService(myFormService, myJupyterService, myKernelService, myVariableService) {
        this.myFormService = myFormService;
        this.myJupyterService = myJupyterService;
        this.myKernelService = myKernelService;
        this.myVariableService = myVariableService;
        this.path = new rxjs_1.BehaviorSubject('scriptedforms_default_path');
        this.baseUrl = this.getApplicationBaseUrl();
    }
    Object.defineProperty(FileService.prototype, "context", {
        set: function (_context) {
            this._context = _context;
            this._context.pathChanged.connect(this.setPathFromContext, this);
        },
        enumerable: true,
        configurable: true
    });
    FileService.prototype.getApplicationBaseUrl = function () {
        var jupyterBaseUrl = JSON.parse(document.getElementById('jupyter-config-data').textContent).baseUrl;
        var application = JSON.parse(document.getElementById('scriptedforms-config-data').textContent).applicationToRun;
        var baseUrl = window.location.protocol + "//" + window.location.host + jupyterBaseUrl + "scriptedforms/" + application + "/";
        console.log(baseUrl);
        return baseUrl;
    };
    FileService.prototype.setNode = function (node) {
        this.node = node;
    };
    FileService.prototype.handleFileContents = function (fileContents) {
        var _this = this;
        var priorOverflow = this.node.scrollTop;
        this.renderComplete = new coreutils_1.PromiseDelegate();
        this.renderComplete.promise.then(function () {
            _this.node.scrollTop = priorOverflow;
        });
        this.myFormService.setTemplate(fileContents);
        return this.renderComplete.promise;
    };
    FileService.prototype.loadFileContents = function (path) {
        var _this = this;
        return this.myJupyterService.contentsManager.get(path).then(function (model) {
            var fileContents = model.content;
            return _this.handleFileContents(fileContents);
        });
    };
    FileService.prototype.setPathFromContext = function () {
        this.path.next(this.context.path);
    };
    FileService.prototype.setPath = function (path) {
        this.path.next(path);
    };
    FileService.prototype.serviceSessionInitialisation = function () {
        console.log('service session initialisation');
        this.myFormService.formInitialisation();
        this.myVariableService.variableInitialisation();
    };
    FileService.prototype.openFile = function (path) {
        var _this = this;
        console.log('open file');
        this.setPath(path);
        this.myKernelService.sessionConnect(path).then(function () {
            _this.serviceSessionInitialisation();
            return _this.loadFileContents(path);
        });
    };
    FileService.prototype.setTemplateToString = function (dummyPath, template) {
        var _this = this;
        this.setPath(dummyPath);
        this.myKernelService.sessionConnect(dummyPath).then(function () {
            _this.serviceSessionInitialisation();
            return _this.handleFileContents(template);
        });
    };
    FileService.prototype.urlToFilePath = function (url) {
        var pattern = RegExp("^" + escapeRegExp(this.baseUrl) + "(.*\\.(md|yaml))");
        var match = pattern.exec(url);
        if (match !== null) {
            return decodeURIComponent(match[1]);
        }
        else {
            return null;
        }
    };
    FileService.prototype.openUrl = function (url) {
        console.log('open url');
        var path = this.urlToFilePath(window.location.href);
        if (path !== null) {
            this.openFile(path);
        }
    };
    FileService = __decorate([
        core_1.Injectable(),
        __metadata("design:paramtypes", [form_service_1.FormService,
            jupyter_service_1.JupyterService,
            kernel_service_1.KernelService,
            variable_service_1.VariableService])
    ], FileService);
    return FileService;
}());
exports.FileService = FileService;
//# sourceMappingURL=file.service.js.map