import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EnvironmentComponent } from './environment.component';
import { EnvClientComponent } from './env-client/env-client.component';
import { EnvServerComponent } from './env-server/env-server.component';
import { EnvWorkerComponent } from './env-worker/env-worker.component';
import { EnvAgentComponent } from './env-agent/env-agent.component';

@NgModule({
  imports: [
    CommonModule
  ],
  declarations: [EnvironmentComponent, EnvClientComponent, EnvServerComponent, EnvWorkerComponent, EnvAgentComponent]
})
export class EnvironmentModule { }
