"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
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
var coreutils_1 = require("@phosphor/coreutils");
var services_1 = require("@jupyterlab/services");
function loadDev(serviceManager) {
    if (serviceManager === void 0) { serviceManager = new services_1.ServiceManager(); }
    // const serviceManager = new ServiceManager();
    runDevModeWatchdog(serviceManager);
}
exports.loadDev = loadDev;
var watchdogDevModeCode = "\nimport os\nfrom watchdog.observers import Observer\nfrom watchdog.events import FileSystemEventHandler, FileModifiedEvent\n\nimport scriptedforms\n\nclass MyHandler(FileSystemEventHandler):\n    def on_modified(self, event):\n        if type(event) == FileModifiedEvent:\n            print(os.path.abspath(event.src_path))\n\nevent_handler = MyHandler()\nobserver = Observer()\nobserver.schedule(\n    event_handler,\n    path=os.path.join(os.path.dirname(scriptedforms.__file__), 'lib'),\n    recursive=True)\nobserver.start()\n";
function runDevModeWatchdog(serviceManager) {
    var sessionReady = new coreutils_1.PromiseDelegate();
    var path = '_dev_watchdog_scriptedforms';
    var settings = services_1.ServerConnection.makeSettings({});
    var startNewOptions = {
        kernelName: 'python3',
        serverSettings: settings,
        path: path
    };
    serviceManager.sessions.findByPath(path).then(function (model) {
        services_1.Session.connectTo(model, settings).then(function (session) {
            sessionReady.resolve(session);
        });
    }).catch(function () {
        services_1.Session.startNew(startNewOptions).then(function (session) {
            session.kernel.requestExecute({ code: watchdogDevModeCode });
            sessionReady.resolve(session);
        });
    });
    sessionReady.promise.then(function (session) {
        session.iopubMessage.connect(function (sender, msg) {
            if (services_1.KernelMessage.isErrorMsg(msg)) {
                var errorMsg = msg;
                console.error(errorMsg.content);
            }
            if (msg.content.text) {
                var content = String(msg.content.text).trim();
                var files = content.split('\n');
                console.log(files);
                location.reload(true);
            }
        });
    });
}
//# sourceMappingURL=dev.js.map