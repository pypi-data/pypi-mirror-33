import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {RouterModule} from "@angular/router";
import {NavbarComponent} from "./navbar.component";

@NgModule({
    exports: [NavbarComponent],
    imports: [
        CommonModule,
        RouterModule
    ],
    declarations: [NavbarComponent],
})
export class NavbarModule {
}
