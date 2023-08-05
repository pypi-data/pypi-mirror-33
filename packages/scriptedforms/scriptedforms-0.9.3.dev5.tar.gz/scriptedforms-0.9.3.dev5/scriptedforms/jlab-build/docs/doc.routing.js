"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var router_1 = require("@angular/router");
var landing_page_component_1 = require("./landing-page/landing-page.component");
var appRoutes = [
    {
        path: '',
        component: landing_page_component_1.LandingPageComponent
    },
    {
        path: '**', component: landing_page_component_1.LandingPageComponent
    }
];
exports.RoutingModule = router_1.RouterModule.forRoot(appRoutes);
//# sourceMappingURL=doc.routing.js.map