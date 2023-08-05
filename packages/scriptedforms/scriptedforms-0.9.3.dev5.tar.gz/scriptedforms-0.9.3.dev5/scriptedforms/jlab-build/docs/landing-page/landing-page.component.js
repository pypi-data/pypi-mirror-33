"use strict";
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
var core_1 = require("@angular/core");
var widgets_1 = require("@phosphor/widgets");
var services_1 = require("@jupyterlab/services");
var widget_1 = require("../../app/widget");
var htmlTemplate = require("html-loader!./landing-page.component.html");
var template = '' + htmlTemplate;
var aTemplate = "\n# Live documentation\n\nThere isn't any docs here yet.\n\nWatch this space.\n\n## Available example forms\n\n<section-start always>\n\n~~~python\nimport urllib.parse\nfrom glob import glob\nfrom IPython.display import display, Markdown\n~~~\n\n</section-start>\n\n<section-filechange onLoad paths=\"['.']\">\n\n~~~python\nfilepaths = glob('*.md') + glob('*/*.md') + glob('*/*/*.md')\nfor filepath in filepaths:\n    escaped_filepath = urllib.parse.quote(filepath)\n    display(Markdown('[{}](../use/{})'.format(filepath, escaped_filepath)))\n~~~\n\n</section-filechange>\n";
var LandingPageComponent = /** @class */ (function () {
    function LandingPageComponent() {
    }
    LandingPageComponent.prototype.ngAfterViewInit = function () {
        var serviceManager = new services_1.ServiceManager();
        var contentsManager = new services_1.ContentsManager();
        var formWidget = new widget_1.ScriptedFormsWidget({
            serviceManager: serviceManager,
            contentsManager: contentsManager
        });
        formWidget.form.initiliseScriptedForms();
        window.onresize = function () { formWidget.update(); };
        widgets_1.Widget.attach(formWidget, this.formWrapper.nativeElement);
        formWidget.form.setTemplateToString('a_dummy_path', aTemplate);
    };
    __decorate([
        core_1.ViewChild('formWrapper'),
        __metadata("design:type", core_1.ElementRef)
    ], LandingPageComponent.prototype, "formWrapper", void 0);
    LandingPageComponent = __decorate([
        core_1.Component({
            selector: 'app-landing-page',
            template: template
        }),
        __metadata("design:paramtypes", [])
    ], LandingPageComponent);
    return LandingPageComponent;
}());
exports.LandingPageComponent = LandingPageComponent;
//# sourceMappingURL=landing-page.component.js.map