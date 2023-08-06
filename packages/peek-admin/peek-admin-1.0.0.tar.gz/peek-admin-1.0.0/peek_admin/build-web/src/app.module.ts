import {BrowserModule} from "@angular/platform-browser";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";

import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {HttpModule} from "@angular/http";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {Ng2BalloonMsgModule} from "@synerty/ng2-balloon-msg-web";
import {
  TupleStorageFactoryService,
  VortexService,
  VortexStatusService,
  WebSqlFactoryService
} from "@synerty/vortexjs";

import {
  TupleStorageFactoryServiceWeb,
  WebSqlBrowserFactoryService
} from "@synerty/vortexjs/index-browser";
import {AppRoutingModule} from "./app/app-routing.module";
import {AppComponent} from "./app/app.component";
import {DashboardModule} from "./app/dashboard/dashboard.module";
import {SettingModule} from "./app/setting/setting.module";
import {NavbarModule} from "./app/navbar/navbar.module";
import {UpdateModule} from "./app/update/update.module";


@NgModule({
    declarations: [
        AppComponent,
    ],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        FormsModule,
        HttpModule,
        AppRoutingModule,
        Ng2BalloonMsgModule,
        DashboardModule,
        SettingModule,
        NavbarModule,
        UpdateModule
    ],
    providers: [
        {provide: WebSqlFactoryService, useClass: WebSqlBrowserFactoryService},
        {provide: TupleStorageFactoryService, useClass: TupleStorageFactoryServiceWeb},
        Ng2BalloonMsgService, VortexService, VortexStatusService],
    bootstrap: [AppComponent]
})
export class AppModule {

}
