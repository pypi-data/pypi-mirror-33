import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app.module';
import { environment } from './environments/environment';

if (environment.production) {
  enableProdMode();
}

import {VortexService} from "@synerty/vortexjs";
let host = location.host.split(':')[0];
VortexService.setVortexUrl(`ws://${host}:8013/vortexws`);
VortexService.setVortexClientName("peek-admin");

platformBrowserDynamic().bootstrapModule(AppModule);
