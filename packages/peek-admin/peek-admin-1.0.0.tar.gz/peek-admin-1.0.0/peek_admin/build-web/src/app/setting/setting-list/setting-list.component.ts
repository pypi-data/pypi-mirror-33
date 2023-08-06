import {Component, OnInit} from "@angular/core";
import {
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader,
    Tuple
} from "@synerty/vortexjs";


class SettingProperty extends Tuple {

    id: number;
    settingId: number;
    key: string;
    type: string;

    int_value: number;
    char_value: string;
    boolean_value: boolean;

    constructor() {
        super('c.s.p.setting.property')
    }
}

@Component({
    selector: 'app-setting-list',
    templateUrl: './setting-list.component.html',
    styleUrls: ['./setting-list.component.css']
})
export class SettingListComponent extends ComponentLifecycleEventEmitter implements OnInit {
    private readonly filt = {
        plugin: "peek_server",
        key: "server.setting.data"
    };

    items: SettingProperty[] = [];

    loader: TupleLoader;

    constructor(vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this, this.filt);

        this.loader.observable.subscribe(
            tuples => this.items = <SettingProperty[]>tuples);
    }

    ngOnInit() {
    }

}
