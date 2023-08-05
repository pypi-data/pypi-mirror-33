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
var jupyter_service_1 = require("./jupyter.service");
var watchdog_service_1 = require("./watchdog.service");
var file_service_1 = require("./file.service");
var toolbar_service_1 = require("./toolbar.service");
var InitialisationService = /** @class */ (function () {
    function InitialisationService(myJupyterService, myFileService, myWatchdogService, myToolbarService) {
        this.myJupyterService = myJupyterService;
        this.myFileService = myFileService;
        this.myWatchdogService = myWatchdogService;
        this.myToolbarService = myToolbarService;
    }
    InitialisationService.prototype.initiliseBaseScriptedForms = function (options) {
        this.myJupyterService.setServiceManager(options.serviceManager);
        this.myJupyterService.setContentsManager(options.contentsManager);
        this.myFileService.setNode(options.node);
        this.myToolbarService.setToolbar(options.toolbar);
        this.myWatchdogService.startWatchdog();
    };
    InitialisationService.prototype.initiliseScriptedForms = function (options) {
        var _this = this;
        console.log('Initialising ScriptedForms');
        this.initiliseBaseScriptedForms(options);
        if (!options.context) {
            console.log('No Widget Context. Assuming in standalone mode.');
            this.myFileService.openUrl(window.location.href);
        }
        else {
            console.log('Widget context found. Assuming running as JupyterLab extension.');
            this.myFileService.context = options.context;
            this.myFileService.openFile(options.context.path);
        }
        if (!options.context) {
            window.onpopstate = function (event) {
                _this.myFileService.openUrl(window.location.href);
            };
        }
    };
    InitialisationService = __decorate([
        core_1.Injectable(),
        __metadata("design:paramtypes", [jupyter_service_1.JupyterService,
            file_service_1.FileService,
            watchdog_service_1.WatchdogService,
            toolbar_service_1.ToolbarService])
    ], InitialisationService);
    return InitialisationService;
}());
exports.InitialisationService = InitialisationService;
//# sourceMappingURL=initialisation.service.js.map