import {NgModule} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {CommonModule} from "@angular/common";
import {UpdateComponent} from "./update.component";
import {UpdatePlatformComponent} from "./update-platform/update-platform.component";
import {UpdatePluginComponent} from "./update-plugin/update-plugin.component";
import {UpdateLicenseComponent} from "./update-license/update-license.component";
import {FileUploadModule} from "ng2-file-upload";

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        FileUploadModule
    ],
    declarations: [UpdateComponent,
        UpdatePlatformComponent,
        UpdatePluginComponent,
        UpdateLicenseComponent
    ]
})
export class UpdateModule {
}
