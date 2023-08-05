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
require("./public-path");
var CONFIG_DIV = document.getElementById('scriptedforms-config-data');
if (CONFIG_DIV) {
    document.body.classList.add('fullscreen-body');
}
require("./polyfills");
require("./vendors/jupyterlab");
require("./vendors/angular");
require("./vendors/misc");
require("hammerjs");
var core_1 = require("@angular/core");
var jupyterlab_plugin_1 = require("./jupyterlab-extension/jupyterlab-plugin");
var app_1 = require("./app");
var docs_1 = require("./docs");
var dev_1 = require("./dev");
if (process.env.NODE_ENV === 'production') {
    console.log('Production Mode: Angular is in production mode.');
    core_1.enableProdMode();
}
function main() {
    var config = JSON.parse(CONFIG_DIV.textContent);
    if (config.applicationToRun === 'use') {
        app_1.loadApp();
    }
    else if (config.applicationToRun === 'docs') {
        docs_1.loadDocs();
    }
    else {
        throw RangeError('Expected docs or use');
    }
}
if (CONFIG_DIV) {
    if (process.env.NODE_ENV !== 'production') {
        console.log('Development Mode: ScriptedForms is watching for JavaScript changes.');
        dev_1.loadDev();
    }
    window.onload = main;
}
exports.default = jupyterlab_plugin_1.plugin;
//# sourceMappingURL=main.js.map