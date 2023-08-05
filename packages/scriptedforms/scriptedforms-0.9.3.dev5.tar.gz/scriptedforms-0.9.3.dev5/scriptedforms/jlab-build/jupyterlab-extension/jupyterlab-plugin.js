"use strict";
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
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
var application_1 = require("@jupyterlab/application");
var coreutils_1 = require("@jupyterlab/coreutils");
var docregistry_1 = require("@jupyterlab/docregistry");
var apputils_1 = require("@jupyterlab/apputils");
var widget_1 = require("./../app/widget");
/*
 *  # Create your own Angular JupyterLab extension (cont.)
 *
 *  This is part of the guide available at
 *  <https://github.com/SimonBiggs/scriptedforms/blob/master/scriptedforms/docs/create-your-own-angular-jupyterlab-extension.md>
 *
 *  ## Defining the JupyterLab extension
 *
 *  Here the JupyterLab extension is defined. The majority of this file is not
 *  unique to an Angular setup. However, there is one section which is of interest.
 *
 *  The "initialiseScriptedForms" function which has been defined on the AngularWrapperWidget
 *  is called within the `createNewWidget` function on the `ScriptedFormsWidgetFactory`.
 *  It is set to execute once the widget context is ready.
 */
var FACTORY = 'ScriptedForms';
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.preview = 'scriptedforms:open';
})(CommandIDs || (CommandIDs = {}));
var ScriptedFormsWidgetFactory = /** @class */ (function (_super) {
    __extends(ScriptedFormsWidgetFactory, _super);
    function ScriptedFormsWidgetFactory(options) {
        var _this = _super.call(this, options) || this;
        _this.serviceManager = options.serviceManager;
        _this.contentsManager = options.contentsManager;
        return _this;
    }
    ScriptedFormsWidgetFactory.prototype.createNewWidget = function (context) {
        var formWidget = new widget_1.ScriptedFormsWidget({
            serviceManager: this.serviceManager,
            contentsManager: this.contentsManager,
            context: context
        });
        formWidget.context.ready.then(function () {
            formWidget.form.initiliseScriptedForms();
        });
        return formWidget;
    };
    return ScriptedFormsWidgetFactory;
}(docregistry_1.ABCWidgetFactory));
exports.ScriptedFormsWidgetFactory = ScriptedFormsWidgetFactory;
function activate(app, restorer, settingRegistry) {
    app.docRegistry.addFileType({
        name: 'scripted-form',
        mimeTypes: ['text/markdown'],
        extensions: ['.form.md'],
        contentType: 'file',
        fileFormat: 'text'
    });
    var factory = new ScriptedFormsWidgetFactory({
        name: FACTORY,
        fileTypes: ['markdown', 'scripted-form'],
        defaultFor: ['scripted-form'],
        readOnly: true,
        serviceManager: app.serviceManager,
        contentsManager: app.serviceManager.contents,
    });
    app.docRegistry.addWidgetFactory(factory);
    var tracker = new apputils_1.InstanceTracker({
        namespace: '@simonbiggs/scriptedforms'
    });
    restorer.restore(tracker, {
        command: 'docmanager:open',
        args: function (widget) { return ({ path: widget.context.path, factory: FACTORY }); },
        name: function (widget) { return widget.context.path; }
    });
    factory.widgetCreated.connect(function (sender, widget) {
        tracker.add(widget);
        widget.context.pathChanged.connect(function () {
            tracker.save(widget);
        });
    });
    app.commands.addCommand(CommandIDs.preview, {
        label: 'ScriptedForms',
        execute: function (args) {
            var path = args['path'];
            if (typeof path !== 'string') {
                return;
            }
            return app.commands.execute('docmanager:open', {
                path: path, factory: FACTORY
            });
        }
    });
}
exports.plugin = {
    id: '@simonbiggs/scriptedforms:plugin',
    autoStart: true,
    requires: [application_1.ILayoutRestorer, coreutils_1.ISettingRegistry],
    activate: activate
};
//# sourceMappingURL=jupyterlab-plugin.js.map