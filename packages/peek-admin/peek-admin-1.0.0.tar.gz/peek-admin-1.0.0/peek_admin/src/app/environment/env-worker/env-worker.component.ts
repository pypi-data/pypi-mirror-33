import { Component, OnInit } from '@angular/core';
import {
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader
} from "@synerty/vortexjs";
import {PeekEnvWorker} from "../env-tuples";

@Component({
  selector: 'app-env-worker',
  templateUrl: './env-worker.component.html',
  styleUrls: ['./env-worker.component.css']
})
export class EnvWorkerComponent extends ComponentLifecycleEventEmitter implements OnInit {


    private readonly filt = {
        plugin: 'peek_server',
        key: "peakadm.env.worker.list.data"
    };

    items: PeekEnvWorker[] = [];
    loader: TupleLoader;

    constructor(vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this,
            () => {
                return this.filt;
            });

        this.loader.observable.subscribe(
            tuples => this.items = <PeekEnvWorker[]>tuples);

    }

  ngOnInit() {
  }

}
