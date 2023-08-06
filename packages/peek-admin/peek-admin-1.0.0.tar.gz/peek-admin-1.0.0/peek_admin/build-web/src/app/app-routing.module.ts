import {NgModule} from "@angular/core";
import {Routes, RouterModule, Route} from "@angular/router";
import {DashboardComponent} from "./dashboard/dashboard.component";
import {UpdateComponent} from "./update/update.component";
import {SettingComponent} from "./setting/setting.component";
import {ComponentLifecycleEventEmitter, Tuple} from "@synerty/vortexjs";
import {pluginAppRoutes} from "../plugin-app-routes";
import {pluginCfgRoutes} from "../plugin-cfg-routes";


export const dashboardRoute: Route = {
    path: '',
    component: DashboardComponent
};

export const settingRoute: Route = {
    path: 'setting',
    component: SettingComponent
};

export const environmentRoute: Route = {
    path: 'environment',
    // component: EnvironmentComponent
};

export const updateRoute: Route = {
    path: 'update',
    component: UpdateComponent
};

const staticRoutes: Routes = [
    dashboardRoute,
    settingRoute,
    // environmentRoute,
    updateRoute,
    {
        path: '**',
        component: DashboardComponent

    }
];



class PluginRoutesTuple extends Tuple {
    constructor() {
        super('peek_server.PluginRoutesTuple');
    }

    pluginName: string;
    lazyLoadModulePath: string;
}


@NgModule({
    imports: [RouterModule.forRoot([
      ...pluginAppRoutes,
      ...pluginCfgRoutes,
      ...staticRoutes
    ])],
    exports: [RouterModule],
    providers: []
})
export class AppRoutingModule extends ComponentLifecycleEventEmitter {
}
