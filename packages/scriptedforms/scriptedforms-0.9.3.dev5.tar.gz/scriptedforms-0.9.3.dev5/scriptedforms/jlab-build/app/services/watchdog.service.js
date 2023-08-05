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
var rxjs_1 = require("rxjs");
var core_1 = require("@angular/core");
var coreutils_1 = require("@phosphor/coreutils");
var services_1 = require("@jupyterlab/services");
var jupyter_service_1 = require("./jupyter.service");
var file_service_1 = require("./file.service");
var watchdog_code_1 = require("./watchdog-code");
var WatchdogService = /** @class */ (function () {
    function WatchdogService(myFileService, myJupyterService) {
        this.myFileService = myFileService;
        this.myJupyterService = myJupyterService;
        // formFirstPassComplete = new PromiseDelegate<void>();
        this.everythingIdle = new coreutils_1.PromiseDelegate();
        this.watchdogError = new rxjs_1.BehaviorSubject(null);
        this.fileChanged = new rxjs_1.BehaviorSubject(null);
    }
    WatchdogService.prototype.startWatchdog = function () {
        var _this = this;
        var path = '_watchdog_scriptedforms';
        var settings = services_1.ServerConnection.makeSettings({});
        var startNewOptions = {
            kernelName: 'python3',
            serverSettings: settings,
            path: path
        };
        this.myJupyterService.serviceManager.sessions.findByPath(path).then(function (model) {
            services_1.Session.connectTo(model, settings).then(function (session) {
                _this.watchdogFormUpdate(session);
            });
        }).catch(function () {
            services_1.Session.startNew(startNewOptions).then(function (session) {
                session.kernel.requestExecute({ code: watchdog_code_1.startWatchdogSessionCode });
                _this.watchdogFormUpdate(session);
            });
        });
    };
    WatchdogService.prototype.watchdogFormUpdate = function (session) {
        var _this = this;
        this.session = session;
        session.iopubMessage.connect(function (sender, msg) {
            if (services_1.KernelMessage.isErrorMsg(msg)) {
                var errorMsg = msg;
                console.error(errorMsg.content);
                _this.watchdogError.next(msg);
            }
            if (msg.content.text) {
                var content = String(msg.content.text).trim();
                var files = content.split('\n');
                console.log(files);
                var path_1 = _this.myFileService.path.getValue();
                var match = files.some(function (item) {
                    return ((item.startsWith('relative: ')) &&
                        ((item.replace('\\', '/') === "relative: " + path_1) || (item.includes('goutputstream'))));
                });
                if (match) {
                    _this.myFileService.loadFileContents(path_1);
                }
                files.forEach(function (item) {
                    var pathOnly = item.replace('absolute: ', '').replace('relative: ', '');
                    _this.fileChanged.next(pathOnly);
                });
            }
        });
        this.myFileService.path.subscribe(function (value) {
            console.log("File service path changed to: " + value);
            _this.addFilepathObserver(value);
        });
    };
    WatchdogService.prototype.addFilepathObserver = function (filepath) {
        console.log("Watchdog service: Adding " + filepath + " to watch list");
        this.session.kernel.requestExecute({ code: watchdog_code_1.addObserverPathCode(filepath) });
    };
    WatchdogService = __decorate([
        core_1.Injectable(),
        __metadata("design:paramtypes", [file_service_1.FileService,
            jupyter_service_1.JupyterService])
    ], WatchdogService);
    return WatchdogService;
}());
exports.WatchdogService = WatchdogService;
//# sourceMappingURL=watchdog.service.js.map