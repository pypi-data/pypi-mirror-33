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
var coreutils_1 = require("@phosphor/coreutils");
var core_1 = require("@angular/core");
var platform_browser_dynamic_1 = require("@angular/platform-browser-dynamic");
/*
 *  # Create your own Angular JupyterLab extension (cont.)
 *
 *  This is part of the guide available at
 *  <https://github.com/SimonBiggs/scriptedforms/blob/master/scriptedforms/docs/create-your-own-angular-jupyterlab-extension.md>
 *
 *  ## The Phosphor Wrapper
 *
 *  Angular's default setup is to be in control of the entire page. Usually there isn't anything
 *  around or 'above' Angular. In this case however the non-Angular application
 *  JupyterLab needs to be above it. This means that Angular's default browser
 *  bootstrapping cannot be used. Therefore
 *  [manual bootstrapping](https://blog.angularindepth.com/how-to-manually-bootstrap-an-angular-application-9a36ccf86429)
 *  is required.
 *
 *  Not only that but we want JupyterLab to see a Phoshor Widget, not an Angular
 *  app.
 *
 *  And lastly, anytime JupyterLab does something which impacts the Angular app
 *  that change needs to be wrapped up within [ngZone](https://angular.io/api/core/NgZone)
 *  which kicks off Angular's brilliant change detection.
 *
 *  So that's what this file does. It creates an Angular Loader to bootstrap
 *  the Angular App, and then a Phosphor Widget is created which calls that loader
 *  while also providing a `run()` function for the purpose of passing actions
 *  into Angular's change detecting ngZone.
 */
var AngularLoader = /** @class */ (function () {
    function AngularLoader(ngModuleRef) {
        this.injector = ngModuleRef.injector;
        this.applicationRef = this.injector.get(core_1.ApplicationRef);
        this.ngZone = this.injector.get(core_1.NgZone);
        this.componentFactoryResolver = this.injector.get(core_1.ComponentFactoryResolver);
    }
    AngularLoader.prototype.attachComponent = function (ngComponent, dom) {
        var _this = this;
        var componentRef;
        this.ngZone.run(function () {
            var componentFactory = _this.componentFactoryResolver.resolveComponentFactory(ngComponent);
            componentRef = componentFactory.create(_this.injector, [], dom);
            _this.applicationRef.attachView(componentRef.hostView);
        });
        return componentRef;
    };
    return AngularLoader;
}());
exports.AngularLoader = AngularLoader;
var AngularWidget = /** @class */ (function (_super) {
    __extends(AngularWidget, _super);
    function AngularWidget(ngComponent, ngModule, options) {
        var _this = _super.call(this, options) || this;
        _this.componentReady = new coreutils_1.PromiseDelegate();
        platform_browser_dynamic_1.platformBrowserDynamic().bootstrapModule(ngModule)
            .then(function (ngModuleRef) {
            _this.angularLoader = new AngularLoader(ngModuleRef);
            _this.ngZone = _this.angularLoader.ngZone;
            _this.componentRef = _this.angularLoader.attachComponent(ngComponent, _this.node);
            _this.componentInstance = _this.componentRef.instance;
            _this.componentReady.resolve(undefined);
        });
        return _this;
    }
    AngularWidget.prototype.run = function (func) {
        var _this = this;
        this.componentReady.promise.then(function () {
            _this.ngZone.run(func);
        });
    };
    AngularWidget.prototype.dispose = function () {
        var _this = this;
        this.ngZone.run(function () {
            _this.componentRef.destroy();
        });
        _super.prototype.dispose.call(this);
    };
    return AngularWidget;
}(widgets_1.Widget));
exports.AngularWidget = AngularWidget;
//# sourceMappingURL=phosphor-angular-loader.js.map