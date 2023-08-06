import { Component, OnInit } from '@angular/core';
import {
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader
} from "@synerty/vortexjs";
import {PeekEnvServer} from "../env-tuples";

@Component({
  selector: 'app-env-server',
  templateUrl: './env-server.component.html',
  styleUrls: ['./env-server.component.css']
})
export class EnvServerComponent extends ComponentLifecycleEventEmitter implements OnInit {


    private readonly filt = {
        plugin: 'peek_server',
        key: "peakadm.env.server.list.data"
    };

    items: PeekEnvServer[] = [];
    loader: TupleLoader;

    constructor(vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this,
            () => {
                return this.filt;
            });

        this.loader.observable.subscribe(
            tuples => this.items = <PeekEnvServer[]>tuples);

    }

  ngOnInit() {
  }

}
