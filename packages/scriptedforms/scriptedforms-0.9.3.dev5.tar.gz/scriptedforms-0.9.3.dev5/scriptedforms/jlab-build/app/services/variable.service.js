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
This will eventually be how the variables are saved.

Not yet implemented.
*/
var rxjs_1 = require("rxjs");
// import { Slot } from '@phosphor/signaling';
var coreutils_1 = require("@phosphor/coreutils");
var services_1 = require("@jupyterlab/services");
var stringify = require("json-stable-stringify");
var uuid = require("uuid");
var core_1 = require("@angular/core");
var kernel_service_1 = require("./kernel.service");
var VariableService = /** @class */ (function () {
    function VariableService(myKernelSevice) {
        this.myKernelSevice = myKernelSevice;
        this.variableHandlerClass = '_VariableHandler';
        this.handlerName = '_scriptedforms_variable_handler';
        this.fetchVariablesCode = "exec(" + this.handlerName + ".fetch_code)";
        this.variableStatus = new rxjs_1.BehaviorSubject(null);
        this.variableHandlerInitialised = false;
    }
    VariableService.prototype.variableInitialisation = function () {
        var _this = this;
        this.variableStore = new rxjs_1.BehaviorSubject({});
        this.oldVariableStore = null;
        this.variableIdentifierMap = {};
        this.variableEvaluateMap = {};
        this.pythonVariables = {};
        this.variableChangedObservable = new rxjs_1.BehaviorSubject(null);
        this.variableComponentStore = {};
        this.executionCount = new rxjs_1.BehaviorSubject(null);
        this.lastCode = new rxjs_1.BehaviorSubject(null);
        this.variableChangeSubscription = null;
        this.myKernelSevice.session.iopubMessage.connect(function (session, msg) {
            if (services_1.KernelMessage.isExecuteInputMsg(msg)) {
                var executeInputMessage = msg;
                _this.executionCount.next(executeInputMessage.content.execution_count);
                _this.lastCode.next(executeInputMessage.content.code);
            }
        });
    };
    VariableService.prototype.startListeningForChanges = function () {
        var _this = this;
        this.variableChangeSubscription = (this.lastCode.subscribe(function (code) {
            if (_this.variableHandlerInitialised) {
                if (code) {
                    var commentRemovedCode = code.replace(/^#.*\n/, '');
                    if (commentRemovedCode !== _this.fetchVariablesCode) {
                        _this.fetchAll();
                    }
                }
            }
        }));
    };
    VariableService.prototype.resetVariableService = function () {
        this.variableHandlerInitialised = false;
        if (this.variableChangeSubscription) {
            this.variableChangeSubscription.unsubscribe();
        }
        this.variableStatus.next('reset');
        this.variableStore.next({});
        this.oldVariableStore = {};
        this.variableComponentStore = {};
        this.variableIdentifierMap = {};
        this.variableEvaluateMap = {};
    };
    VariableService.prototype.allVariablesInitilised = function () {
        var _this = this;
        var initilisationComplete = new coreutils_1.PromiseDelegate();
        this.variableStatus.next('initialising');
        var jsonEvaluateMap = JSON.stringify(this.variableEvaluateMap);
        var initialiseHandlerCode = this.handlerName + " = " + this.variableHandlerClass + "(\"\"\"" + jsonEvaluateMap + "\"\"\", \"" + this.handlerName + "\")";
        this.myKernelSevice.runCode(initialiseHandlerCode, '"initialiseVariableHandler"')
            .then(function (future) {
            if (future) {
                future.done.then(function () {
                    initilisationComplete.resolve(null);
                    _this.variableHandlerInitialised = true;
                    _this.fetchAll();
                });
            }
            else {
                console.log('No future returned from initialiseVariableHandler');
            }
        });
        return initilisationComplete.promise;
    };
    VariableService.prototype.appendToIdentifierMap = function (variableIdentifier, variableName) {
        this.variableIdentifierMap[variableIdentifier] = variableName;
    };
    VariableService.prototype.appendToEvaluateMap = function (variableName, variableEvaluate) {
        if (!(variableName in this.variableEvaluateMap)) {
            this.variableEvaluateMap[variableName] = variableEvaluate;
        }
    };
    VariableService.prototype.initialiseVariableComponent = function (component) {
        var variableIdentifier = component.variableIdentifier;
        this.variableComponentStore[variableIdentifier] = component;
        var variableEvaluate = component.pythonVariableEvaluate();
        var variableName = component.variableName;
        this.appendToIdentifierMap(variableIdentifier, variableName);
        this.appendToEvaluateMap(variableName, variableEvaluate);
    };
    VariableService.prototype.convertToVariableStore = function (textContent) {
        var result = JSON.parse(textContent);
        this.pythonVariables = result;
        var newVariableStore = {};
        Object.entries(this.variableIdentifierMap).forEach(function (_a) {
            var variableIdentifier = _a[0], variableName = _a[1];
            newVariableStore[variableIdentifier] = result[variableName];
        });
        this.variableStore.next(newVariableStore);
    };
    VariableService.prototype.ifJsonString = function (string) {
        try {
            JSON.parse(string);
        }
        catch (err) {
            return false;
        }
        return true;
    };
    VariableService.prototype.fetchAll = function (label) {
        var _this = this;
        if (label === void 0) { label = '"fetchAllVariables"'; }
        if (!this.variableHandlerInitialised) {
            console.log('fetch called before ready');
            return Promise.resolve(null);
        }
        this.variableStatus.next('fetching');
        var fetchComplete = new coreutils_1.PromiseDelegate();
        this.myKernelSevice.runCode(this.fetchVariablesCode, label)
            .then(function (future) {
            if (future) {
                var textContent_1 = '';
                future.onIOPub = (function (msg) {
                    if (msg.content.text) {
                        textContent_1 = textContent_1.concat(String(msg.content.text));
                        if (_this.ifJsonString(textContent_1)) {
                            _this.convertToVariableStore(textContent_1);
                            _this.checkForChanges();
                        }
                    }
                });
                future.done.then(function () {
                    fetchComplete.resolve(null);
                });
            }
        });
        return fetchComplete.promise;
    };
    VariableService.prototype.updateComponentView = function (component, value) {
        component.updateVariableView(JSON.parse(JSON.stringify(value)));
    };
    VariableService.prototype.variableHasChanged = function (identifier) {
        this.updateComponentView(this.variableComponentStore[identifier], this.variableStore.getValue()[identifier].value);
    };
    VariableService.prototype.checkForChanges = function () {
        var _this = this;
        this.variableStatus.next('checking-for-changes');
        var variableIdentifiers = Object.keys(this.variableComponentStore);
        for (var _i = 0, variableIdentifiers_1 = variableIdentifiers; _i < variableIdentifiers_1.length; _i++) {
            var identifier = variableIdentifiers_1[_i];
            if (this.variableStore.getValue()[identifier].defined) {
                if (this.oldVariableStore) {
                    if (stringify(this.variableStore.getValue()[identifier]) !==
                        stringify(this.oldVariableStore[identifier])) {
                        this.variableHasChanged(identifier);
                    }
                }
                else {
                    this.variableHasChanged(identifier);
                }
            }
        }
        var aVariableHasChanged = (stringify(this.variableStore.getValue()) !==
            stringify(this.oldVariableStore));
        if (aVariableHasChanged) {
            this.variableChangedObservable.next(this.variableStore.getValue());
            this.variableStatus.next('a-change-was-made');
        }
        else {
            this.variableStatus.next('no-change-was-made');
        }
        var id = uuid.v4();
        var staticStatus = 'prepping-for-idle: ' + id;
        this.variableStatus.next(staticStatus);
        this.myKernelSevice.queue.then(function () {
            if (_this.variableStatus.getValue() === staticStatus) {
                _this.variableStatus.next('idle');
            }
        });
        this.oldVariableStore = JSON.parse(JSON.stringify(this.variableStore.getValue()));
    };
    VariableService.prototype.pushVariable = function (variableIdentifier, variableName, valueReference) {
        var pushCode = variableName + " = " + valueReference;
        this.oldVariableStore[variableIdentifier] = {
            defined: true,
            value: JSON.parse(JSON.stringify(valueReference))
        };
        return this.myKernelSevice.runCode(pushCode, '"push"_"' + variableIdentifier + '"').then(function (future) {
            if (future) {
                var promise = future.done;
                return promise;
            }
            else {
                return Promise.resolve('ignore');
            }
        });
    };
    VariableService = __decorate([
        core_1.Injectable(),
        __metadata("design:paramtypes", [kernel_service_1.KernelService])
    ], VariableService);
    return VariableService;
}());
exports.VariableService = VariableService;
//# sourceMappingURL=variable.service.js.map