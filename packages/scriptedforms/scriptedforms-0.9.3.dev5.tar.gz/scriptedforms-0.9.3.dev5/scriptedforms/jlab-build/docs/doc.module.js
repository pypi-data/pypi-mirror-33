"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
var platform_browser_1 = require("@angular/platform-browser");
var core_1 = require("@angular/core");
var animations_1 = require("@angular/platform-browser/animations");
var material_module_1 = require("../vendors/material.module");
var app_module_1 = require("../app/app.module");
var doc_routing_1 = require("./doc.routing");
var doc_component_1 = require("./doc.component");
var landing_page_component_1 = require("./landing-page/landing-page.component");
var DocModule = /** @class */ (function () {
    function DocModule() {
    }
    DocModule = __decorate([
        core_1.NgModule({
            declarations: [
                doc_component_1.DocComponent,
                landing_page_component_1.LandingPageComponent
            ],
            imports: [
                platform_browser_1.BrowserModule,
                animations_1.BrowserAnimationsModule,
                doc_routing_1.RoutingModule,
                material_module_1.MaterialModule,
                app_module_1.AppModule
            ],
            providers: [],
            bootstrap: [doc_component_1.DocComponent]
        })
    ], DocModule);
    return DocModule;
}());
exports.DocModule = DocModule;
//# sourceMappingURL=doc.module.js.map