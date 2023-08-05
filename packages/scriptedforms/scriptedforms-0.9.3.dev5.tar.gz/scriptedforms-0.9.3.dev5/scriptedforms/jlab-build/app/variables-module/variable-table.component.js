"use strict";
// Scripted Forms -- Making GUIs easy for everyone on your team.
// Copyright (C) 2017 Simon Biggs
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
var core_1 = require("@angular/core");
var material_1 = require("@angular/material");
var stringify = require("json-stable-stringify");
var variable_base_component_1 = require("./variable-base.component");
var variable_parameter_component_1 = require("./variable-parameter.component");
// JupyterLab doesn't have custom webpack loaders. Need to be able to
// inline the loaders so that they get picked up without having access to the
// webpack.config.js file
// See https://github.com/jupyterlab/jupyterlab/pull/4334#issuecomment-383104318
var htmlTemplate = require("html-loader!./variable-table.component.html");
// This is currently needed to silence the angular-language-service not finding
// a template for this component.
// Idealy I shall create a pull request which will enable the angular lanugage
// service to detect the template loading method given above.
var template = '' + htmlTemplate;
var VariableTableComponent = /** @class */ (function (_super) {
    __extends(VariableTableComponent, _super);
    function VariableTableComponent() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        _this.typeEdit = null;
        _this.definedInputTypes = {};
        _this.definedDropdownItems = {};
        _this.tableIndex = [];
        _this.availableTypes = ['string', 'number', 'integer', 'boolean'];
        _this.types = [];
        _this.columnDefs = [];
        _this.oldColumnDefs = [];
        _this.dataSource = new material_1.MatTableDataSource();
        _this.isPandas = true;
        _this.focus = [null, null];
        return _this;
    }
    VariableTableComponent.prototype.ngAfterViewInit = function () {
        var _this = this;
        if (this.inputTypes) {
            if (this.variableInputTypes.variableValue) {
                this.definedInputTypes = this.variableInputTypes.variableValue;
            }
            this.variableInputTypes.variableChange.asObservable().subscribe(function (value) {
                if (value) {
                    _this.definedInputTypes = value;
                    // console.log(`Input Type: ${this.definedInputTypes}`);
                    // console.log(this.definedInputTypes);
                }
            });
        }
        if (this.dropdownItems) {
            if (this.variableDropdownItems.variableValue) {
                this.definedDropdownItems = this.variableDropdownItems.variableValue;
            }
            this.variableDropdownItems.variableChange.asObservable().subscribe(function (value) {
                if (value) {
                    _this.definedDropdownItems = value;
                    // console.log(`Dropdown Items: ${this.definedDropdownItems}`);
                    // console.log(this.definedDropdownItems);
                }
            });
        }
        _super.prototype.ngAfterViewInit.call(this);
    };
    VariableTableComponent.prototype.updateVariableView = function (value) {
        var _this = this;
        var numRowsUnchanged;
        if (this.variableValue) {
            numRowsUnchanged = (value.data.length === this.variableValue.data.length);
        }
        else {
            numRowsUnchanged = false;
        }
        this.variableValue = value;
        var columns = [];
        var types = [];
        this.variableValue.schema.fields.forEach(function (field) {
            columns.push(field.name);
            if (_this.availableTypes.includes(field.type)) {
                types.push(field.type);
            }
            else {
                types.push('string');
            }
        });
        this.oldColumnDefs = this.columnDefs;
        this.columnDefs = columns;
        this.types = types;
        var primaryKey = this.variableValue.schema.primaryKey;
        var tableIndex = [];
        this.variableValue.data.forEach(function (row) {
            tableIndex.push(row[primaryKey]);
        });
        this.tableIndex = tableIndex;
        var columnsUnchanged = (this.oldColumnDefs.length === this.columnDefs.length &&
            this.columnDefs.every(function (item, index) { return item === _this.oldColumnDefs[index]; }));
        if (columnsUnchanged && numRowsUnchanged) {
            types.forEach(function (type, index) {
                if (_this.oldVariableValue.schema.fields[index].type !== type) {
                    _this.oldVariableValue.schema.fields[index].type = type;
                }
            });
            this.variableValue.data.forEach(function (row, i) {
                var keys = Object.keys(row);
                keys.forEach(function (key, j) {
                    if ((i !== _this.focus[0]) || (key !== _this.focus[1])) {
                        if (_this.oldVariableValue.data[i][key] !== row[key]) {
                            // console.log([this.variableIdentifier, i, key]);
                            _this.dataSource.data[i][key] = row[key];
                            _this.oldVariableValue.data[i][key] = row[key];
                        }
                    }
                });
            });
        }
        else {
            this.dataSource.data = this.variableValue.data;
            this.updateOldVariable();
        }
    };
    VariableTableComponent.prototype.dataChanged = function () {
        this.variableValue.data = JSON.parse(JSON.stringify(this.dataSource.data));
        this.variableChanged();
    };
    VariableTableComponent.prototype.typesChanged = function () {
        var _this = this;
        var didDataChange = false;
        this.variableValue.schema.fields.forEach(function (field, index) {
            if (_this.oldVariableValue.schema.fields[index].type === 'boolean' && _this.types[index] === 'string') {
                _this.dataSource.data.forEach(function (row) {
                    row[_this.columnDefs[index]] = '';
                    didDataChange = true;
                });
            }
            field.type = _this.types[index];
        });
        if (didDataChange) {
            this.variableValue.data = JSON.parse(JSON.stringify(this.dataSource.data));
        }
        this.variableChanged();
    };
    VariableTableComponent.prototype.testIfDifferent = function () {
        return !(stringify(this.variableValue) === stringify(this.oldVariableValue));
    };
    VariableTableComponent.prototype.pythonValueReference = function () {
        return "_json_table_to_df(r'" + JSON.stringify(this.variableValue) + "')";
    };
    VariableTableComponent.prototype.pythonVariableEvaluate = function () {
        return "json.loads(" + this.variableName + ".to_json(orient='table'))";
    };
    VariableTableComponent.prototype.onBlur = function (tableCoords) {
        this.focus = [null, null];
    };
    VariableTableComponent.prototype.onFocus = function (tableCoords) {
        this.focus = tableCoords;
    };
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], VariableTableComponent.prototype, "typeEdit", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], VariableTableComponent.prototype, "inputTypes", void 0);
    __decorate([
        core_1.Input(),
        __metadata("design:type", String)
    ], VariableTableComponent.prototype, "dropdownItems", void 0);
    __decorate([
        core_1.ViewChild('variableInputTypes'),
        __metadata("design:type", variable_parameter_component_1.VariableParameterComponent)
    ], VariableTableComponent.prototype, "variableInputTypes", void 0);
    __decorate([
        core_1.ViewChild('variableDropdownItems'),
        __metadata("design:type", variable_parameter_component_1.VariableParameterComponent)
    ], VariableTableComponent.prototype, "variableDropdownItems", void 0);
    VariableTableComponent = __decorate([
        core_1.Component({
            selector: 'variable-table',
            template: template,
            styles: [
                "\n.container {\n  display: flex;\n  flex-direction: column;\n  min-width: 300px;\n}\n\n.mat-form-field {\n  width: 100%;\n}\n"
            ]
        })
    ], VariableTableComponent);
    return VariableTableComponent;
}(variable_base_component_1.VariableBaseComponent));
exports.VariableTableComponent = VariableTableComponent;
//# sourceMappingURL=variable-table.component.js.map