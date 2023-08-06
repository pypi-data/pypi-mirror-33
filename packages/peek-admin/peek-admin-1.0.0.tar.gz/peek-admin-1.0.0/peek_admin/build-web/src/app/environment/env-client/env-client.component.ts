import { Component, OnInit } from '@angular/core';
import {
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader
} from "@synerty/vortexjs";
import {PeekEnvClient} from "../env-tuples";

@Component({
  selector: 'app-env-client',
  templateUrl: './env-client.component.html',
  styleUrls: ['./env-client.component.css']
})
export class EnvClientComponent extends ComponentLifecycleEventEmitter implements OnInit {


    private readonly filt = {
        plugin: 'peek_server',
        key: "peakadm.env.client.list.data"
    };

    items: PeekEnvClient[] = [];
    loader: TupleLoader;

    constructor(vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this,
            () => {
                return this.filt;
            });

        this.loader.observable.subscribe(
            tuples => this.items = <PeekEnvClient[]>tuples);

    }

  ngOnInit() {
  }

}
