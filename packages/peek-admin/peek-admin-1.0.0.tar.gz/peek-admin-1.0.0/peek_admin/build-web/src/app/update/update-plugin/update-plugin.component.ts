import {Component, OnInit, Input} from "@angular/core";
import {
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader,
    Tuple,
    Payload
} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {FileUploader} from "ng2-file-upload";

class PeekPluginInfo extends Tuple {
    constructor() {
        super('peek_server.plugin.info')
    }

    id: number;
    title: string;
    name: string;
    version: string;
    creator: string | null;
    website: string | null;
    buildNumber: string | null;
    buildDate: string | null;

}


@Component({
    selector: 'app-update-plugin',
    templateUrl: './update-plugin.component.html',
    styleUrls: ['./update-plugin.component.css']
})
export class UpdatePluginComponent extends ComponentLifecycleEventEmitter implements OnInit {
    private readonly filt = {
        plugin: 'peek_server',
        key: "peek_server.plugin.version.info"
    };

    items: PeekPluginInfo[] = [];

    loader: TupleLoader;

    @Input()
    licenced: boolean = false;

    serverRestarting: boolean = false;
    progressPercentage: string = '';

    uploader: FileUploader = new FileUploader({
        url: '/peek_server.update.plugin',
        isHTML5: true,
        disableMultipart: true,
        queueLimit: 1,
        method: 'POST',
        autoUpload: true,
        removeAfterUpload: false
    });
    hasBaseDropZoneOver: boolean = false;

    constructor(private vortexService: VortexService,
                private balloonMsg: Ng2BalloonMsgService) {
        super();

        this.doCheckEvent.subscribe(() => this.checkProgress());

        this.loader = vortexService.createTupleLoader(this, this.filt);

        this.loader.observable.subscribe(
            tuples => this.items = <PeekPluginInfo[]>tuples);
    }

    ngOnInit() {
    }

    uploadEnabled() {
        return this.licenced && this.uploader.queue.length == 0;
    }

    checkProgress() {
        this.progressPercentage = '';

        if (this.uploader.queue.length != 1)
            return;

        let fileItem = this.uploader.queue[0];
        if (fileItem._xhr == null)
            return;

        let status = fileItem._xhr.status;
        let responseJsonStr = fileItem._xhr.responseText;

        if (!status || status == 200 && !responseJsonStr.length) {
            this.progressPercentage = fileItem.progress + '%';
            return;
        }

        if (status == 200) {
            let data = JSON.parse(responseJsonStr);

            this.progressPercentage = '';
            if (data.error) {
                this.balloonMsg.showError("Peek App Update Failed\n" + data.error);
            } else {
                this.serverRestarting = true;
                this.balloonMsg.showSuccess("Peek App Update Complete<br/>New version is "
                    + data.message + "<br/><br/Plugin will be restarted");
            }

        } else {
            this.progressPercentage = '';
            this.balloonMsg.showError("Peek App Update Failed<br/> Status : " + status);
        }

        this.uploader.removeFromQueue(fileItem);
    }


    fileOverBase(e: any): void {
        this.hasBaseDropZoneOver = e;
    }

}



