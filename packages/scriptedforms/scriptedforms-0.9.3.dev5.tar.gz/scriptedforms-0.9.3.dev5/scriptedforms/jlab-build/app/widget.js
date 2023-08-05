"use strict";
/*
 *  Copyright 2017 Simon Biggs
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
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
Object.defineProperty(exports, "__esModule", { value: true });
var widgets_1 = require("@phosphor/widgets");
var apputils_1 = require("@jupyterlab/apputils");
var coreutils_1 = require("@jupyterlab/coreutils");
var phosphor_angular_loader_1 = require("./phosphor-angular-loader");
var app_component_1 = require("./app.component");
var app_module_1 = require("./app.module");
var AngularWrapperWidget = /** @class */ (function (_super) {
    __extends(AngularWrapperWidget, _super);
    function AngularWrapperWidget(options) {
        var _this = _super.call(this, app_component_1.AppComponent, app_module_1.AppModule) || this;
        _this.scriptedFormsOptions = Object.assign({
            node: _this.node
        }, options);
        return _this;
    }
    AngularWrapperWidget.prototype.initiliseScriptedForms = function () {
        var _this = this;
        this.run(function () {
            _this.componentInstance.initiliseScriptedForms(_this.scriptedFormsOptions);
        });
    };
    AngularWrapperWidget.prototype.initiliseBaseScriptedForms = function () {
        var _this = this;
        this.run(function () {
            _this.componentInstance.initiliseBaseScriptedForms(_this.scriptedFormsOptions);
        });
    };
    AngularWrapperWidget.prototype.setTemplateToString = function (dummyPath, template) {
        var _this = this;
        this.run(function () {
            _this.componentInstance.setTemplateToString(dummyPath, template);
        });
    };
    return AngularWrapperWidget;
}(phosphor_angular_loader_1.AngularWidget));
exports.AngularWrapperWidget = AngularWrapperWidget;
var ScriptedFormsWidget = /** @class */ (function (_super) {
    __extends(ScriptedFormsWidget, _super);
    function ScriptedFormsWidget(options) {
        var _this = _super.call(this) || this;
        if (options.context) {
            _this._context = options.context;
            _this.onPathChanged();
            _this._context.pathChanged.connect(_this.onPathChanged, _this);
        }
        _this.addClass('scripted-form-widget');
        var layout = (_this.layout = new widgets_1.BoxLayout());
        var toolbar = new apputils_1.Toolbar();
        toolbar.addClass('jp-NotebookPanel-toolbar');
        toolbar.addClass('custom-toolbar');
        layout.addWidget(toolbar);
        widgets_1.BoxLayout.setStretch(toolbar, 0);
        var angularWrapperWidgetOptions = Object.assign({ toolbar: toolbar }, options);
        _this.form = new AngularWrapperWidget(angularWrapperWidgetOptions);
        _this.form.addClass('form-container');
        layout.addWidget(_this.form);
        widgets_1.BoxLayout.setStretch(_this.form, 1);
        return _this;
    }
    Object.defineProperty(ScriptedFormsWidget.prototype, "ready", {
        get: function () {
            return Promise.resolve();
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ScriptedFormsWidget.prototype, "context", {
        get: function () {
            return this._context;
        },
        enumerable: true,
        configurable: true
    });
    ScriptedFormsWidget.prototype.onPathChanged = function () {
        this.title.label = coreutils_1.PathExt.basename(this._context.path);
    };
    ScriptedFormsWidget.prototype.dispose = function () {
        this.form.dispose();
        _super.prototype.dispose.call(this);
    };
    return ScriptedFormsWidget;
}(widgets_1.Widget));
exports.ScriptedFormsWidget = ScriptedFormsWidget;
//# sourceMappingURL=widget.js.map