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
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = y[op[0] & 2 ? "return" : op[0] ? "throw" : "next"]) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [0, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
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
This service handles all communication to the Python Kernel.

It defines a queue with the aim to only ever send one request to the kernel
at a time and in a well defined order. This queue also handles dropping repeat
requests if the kernel is busy.
*/
var rxjs_1 = require("rxjs");
var core_1 = require("@angular/core");
var coreutils_1 = require("@phosphor/coreutils");
var services_1 = require("@jupyterlab/services");
var jupyter_service_1 = require("./jupyter.service");
function jupyterSessionConnect(serviceManager, path) {
    var promiseDelegate = new coreutils_1.PromiseDelegate();
    serviceManager.sessions.findByPath(path)
        .then(function (sessionModel) {
        serviceManager.sessions.connectTo(sessionModel)
            .then(function (session) { return promiseDelegate.resolve(session); });
    })
        .catch(function () {
        connectToNewSession(serviceManager, path)
            .then(function (session) { return promiseDelegate.resolve(session); });
    });
    return promiseDelegate.promise;
}
function connectToNewSession(serviceManager, path) {
    var promiseDelegate = new coreutils_1.PromiseDelegate();
    var settings = services_1.ServerConnection.makeSettings({});
    var startNewOptions = {
        kernelName: 'python3',
        serverSettings: settings,
        path: path
    };
    serviceManager.sessions.startNew(startNewOptions)
        .then(function (session) { return promiseDelegate.resolve(session); });
    return promiseDelegate.promise;
}
var KernelService = /** @class */ (function () {
    function KernelService(myJupyterService) {
        this.myJupyterService = myJupyterService;
        this.kernelStatus = new rxjs_1.BehaviorSubject(null);
        this.jupyterError = new rxjs_1.BehaviorSubject(null);
        this.queueLength = new rxjs_1.BehaviorSubject(null);
    }
    KernelService.prototype.sessionConnect = function (path) {
        var _this = this;
        var sessionConnected = new coreutils_1.PromiseDelegate();
        jupyterSessionConnect(this.myJupyterService.serviceManager, path)
            .then(function (session) {
            console.log("Connection request to Jupyter Session: " + path);
            _this.session = session;
            _this.kernel = session.kernel;
            _this.queueId = 0;
            _this.queueLog = {};
            _this.queue = Promise.resolve(null);
            _this.runCode('# KernelTest', '"KernelTest"').then(function (future) {
                future.done.then(function () { return sessionConnected.resolve(session); });
            });
            session.iopubMessage.connect(function (_, msg) {
                if (services_1.KernelMessage.isErrorMsg(msg)) {
                    var errorMsg = msg;
                    console.error(errorMsg.content);
                    _this.jupyterError.next(msg);
                }
                if (services_1.KernelMessage.isStatusMsg(msg)) {
                    _this.kernelStatus.next(msg.content.execution_state);
                }
            });
        });
        return sessionConnected.promise;
    };
    KernelService.prototype.queueReset = function () {
        console.log('queue reset');
        this.queueId = 0;
        this.queueLog = {};
        this.queue = Promise.resolve(null);
    };
    KernelService.prototype.restartKernel = function () {
        var _this = this;
        var sessionConnected = new coreutils_1.PromiseDelegate();
        this.kernel.restart().then(function () {
            // this.queueReset();
            sessionConnected.resolve(_this.session);
        });
        return sessionConnected.promise;
    };
    KernelService.prototype.addToQueue = function (name, asyncFunction) {
        var _this = this;
        if (name) {
            console.log("queue: add " + name);
        }
        var currentQueueId = this.queueId;
        this.queueLog[currentQueueId] = name;
        this.queueId += 1;
        var previous = this.queue;
        return this.queue = (function () { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, previous];
                    case 1:
                        _a.sent();
                        delete this.queueLog[currentQueueId];
                        return [2 /*return*/, asyncFunction(currentQueueId)];
                }
            });
        }); })();
    };
    KernelService.prototype.runCode = function (code, name) {
        var _this = this;
        var future;
        var runCode;
        var currentQueue = this.addToQueue(name, function (id) { return __awaiter(_this, void 0, void 0, function () {
            var _this = this;
            var key, addCommentCode;
            return __generator(this, function (_a) {
                runCode = true;
                for (key in this.queueLog) {
                    if (Number(key) > id && this.queueLog[key] === name) {
                        runCode = false;
                        break;
                    }
                }
                if (runCode) {
                    console.log("queue: run " + name);
                    addCommentCode = "# " + name + "\n" + code;
                    future = this.kernel.requestExecute({ code: addCommentCode });
                    future.done.then(function () {
                        _this.queueLength.next(Object.keys(_this.queueLog).length);
                    });
                    return [2 /*return*/, future];
                }
                else {
                    return [2 /*return*/, Promise.resolve()];
                }
                return [2 /*return*/];
            });
        }); }).catch(function (err) {
            console.error(err);
        });
        this.addToQueue(null, function (id) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!runCode) return [3 /*break*/, 2];
                        return [4 /*yield*/, future.done];
                    case 1: return [2 /*return*/, _a.sent()];
                    case 2: return [2 /*return*/, Promise.resolve()];
                }
            });
        }); });
        return currentQueue;
    };
    KernelService = __decorate([
        core_1.Injectable(),
        __metadata("design:paramtypes", [jupyter_service_1.JupyterService])
    ], KernelService);
    return KernelService;
}());
exports.KernelService = KernelService;
//# sourceMappingURL=kernel.service.js.map