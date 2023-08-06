import {Component, OnInit} from "@angular/core";
import {
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader
} from "@synerty/vortexjs";
import {PeekEnvAgent} from "../env-tuples";

@Component({
    selector: 'app-env-agent',
    templateUrl: './env-agent.component.html',
    styleUrls: ['./env-agent.component.css']
})
export class EnvAgentComponent extends ComponentLifecycleEventEmitter implements OnInit {


    private readonly filt = {
        plugin: 'peek_server',
        key: "peakadm.env.agent.list.data"
    };

    items: PeekEnvAgent[] = [];
    loader: TupleLoader;

    constructor(vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this,
            () => {
                return this.filt;
            });

        this.loader.observable.subscribe(
            tuples => this.items = <PeekEnvAgent[]>tuples);

    }

    ngOnInit() {
    }

}
