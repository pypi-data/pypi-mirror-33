"use strict";
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
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
/*
A component that clobbers the html <code> tags.

Markdown turns the following syntax into <code> tags:
```
code here
```

This component highjacks those tags, reads the text written within them and
preps the code for sending to the Python kernel.

The function 'runCode' can be called on this component to have its code sent
to the Python kernel.
*/
// import { BehaviorSubject } from 'rxjs/BehaviorSubject';
// import { Subscription } from 'rxjs/Subscription';
var core_1 = require("@angular/core");
var coreutils_1 = require("@phosphor/coreutils");
var rendermime_1 = require("@jupyterlab/rendermime");
var outputarea_1 = require("@jupyterlab/outputarea");
var codemirror_1 = require("@jupyterlab/codemirror");
var kernel_service_1 = require("../services/kernel.service");
var CodeComponent = /** @class */ (function () {
    function CodeComponent(myKernelSevice, _eRef) {
        var _this = this;
        this.myKernelSevice = myKernelSevice;
        this._eRef = _eRef;
        this._displayIdMap = new Map();
        this.renderMime = new rendermime_1.RenderMimeRegistry({
            initialFactories: rendermime_1.standardRendererFactories,
            sanitizer: {
                sanitize: function (input) { return input; }
            }
        });
        this.model = new outputarea_1.OutputAreaModel();
        this.outputAreaOptions = {
            model: this.model,
            rendermime: this.renderMime
        };
        this.outputArea = new outputarea_1.OutputArea(this.outputAreaOptions);
        // Extract from @jupyterlab/outputarea/src/widget.ts
        this._onIOPub = function (msg) {
            var model = _this.model;
            var msgType = msg.header.msg_type;
            var output;
            var transient = (msg.content.transient || {});
            var displayId = transient['display_id'];
            var targets;
            switch (msgType) {
                case 'execute_result':
                case 'display_data':
                case 'stream':
                case 'error':
                    output = msg.content;
                    output.output_type = msgType;
                    model.add(output);
                    break;
                case 'clear_output':
                    var wait = msg.content.wait;
                    model.clear(wait);
                    break;
                case 'update_display_data':
                    output = msg.content;
                    output.output_type = 'display_data';
                    targets = _this._displayIdMap.get(displayId);
                    if (targets) {
                        for (var _i = 0, targets_1 = targets; _i < targets_1.length; _i++) {
                            var index = targets_1[_i];
                            model.set(index, output);
                        }
                    }
                    break;
                default:
                    break;
            }
            if (msgType === 'display_data' || msgType === 'stream' || msgType === 'update_display_data') {
                _this.firstDisplay.resolve(null);
            }
            if (displayId && msgType === 'display_data') {
                targets = _this._displayIdMap.get(displayId) || [];
                targets.push(model.length - 1);
                _this._displayIdMap.set(displayId, targets);
            }
            // this.onIOPub.next(msg);
        };
    }
    CodeComponent.prototype.updateOutputAreaModel = function () {
        this.outputAreaOptions = {
            model: this.model,
            rendermime: this.renderMime
        };
        this.outputAreaDispose();
        this.outputArea = new outputarea_1.OutputArea(this.outputAreaOptions);
    };
    CodeComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        this.code = this.codecontainer.nativeElement.innerText;
        // Apply python syntax highlighting to every code block
        codemirror_1.Mode.ensure('python').then(function (spec) {
            var el = document.createElement('div');
            codemirror_1.Mode.run(_this.code, spec.mime, el);
            _this.codecontainer.nativeElement.innerHTML = el.innerHTML;
            _this._eRef.nativeElement.classList.add('cm-s-jupyter');
        });
        var element = this._eRef.nativeElement;
        this.outputContainer = document.createElement('div');
        this.outputContainer.appendChild(this.outputArea.node);
        element.parentNode.parentNode.insertBefore(this.outputContainer, element.parentNode);
    };
    CodeComponent.prototype.outputAreaDispose = function () {
        var _this = this;
        if (this.outputArea.future) {
            this.outputArea.future.done.then(function () {
                _this.outputArea.dispose();
            });
        }
        else {
            this.outputArea.dispose();
        }
    };
    CodeComponent.prototype.ngOnDestroy = function () {
        this.outputAreaDispose();
    };
    /**
     * Run the code within the code component. Update the output area with the results of the
     * code.
     */
    CodeComponent.prototype.runCode = function () {
        var _this = this;
        var codeCompleted = new coreutils_1.PromiseDelegate();
        this.promise = this.myKernelSevice.runCode(this.code, this.name);
        this.promise.then(function (future) {
            if (future) {
                _this.firstDisplay = new coreutils_1.PromiseDelegate();
                _this.model = new outputarea_1.OutputAreaModel();
                future.onIOPub = _this._onIOPub;
                future.done.then(function () {
                    codeCompleted.resolve(null);
                });
                _this.firstDisplay.promise.then(function () {
                    _this.updateOutputAreaModel();
                    _this.outputContainer.replaceChild(_this.outputArea.node, _this.outputContainer.firstChild);
                    var element = _this.outputContainer;
                    element.style.minHeight = String(_this.outputArea.node.clientHeight) + 'px';
                });
            }
            else {
                codeCompleted.resolve(null);
            }
        });
        return codeCompleted.promise;
    };
    __decorate([
        core_1.ViewChild('codecontainer'),
        __metadata("design:type", core_1.ElementRef)
    ], CodeComponent.prototype, "codecontainer", void 0);
    CodeComponent = __decorate([
        core_1.Component({
            selector: 'code.language-python',
            template: "<span #codecontainer [hidden]=\"this.name !== undefined\"><ng-content></ng-content></span>"
        }),
        __metadata("design:paramtypes", [kernel_service_1.KernelService,
            core_1.ElementRef])
    ], CodeComponent);
    return CodeComponent;
}());
exports.CodeComponent = CodeComponent;
//# sourceMappingURL=code.component.js.map