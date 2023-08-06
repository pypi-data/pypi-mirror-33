import {Component, OnInit, Input} from "@angular/core";
import {VortexService, ComponentLifecycleEventEmitter} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {FileUploader} from "ng2-file-upload";

@Component({
    selector: 'app-update-platform',
    templateUrl: './update-platform.component.html',
    styleUrls: ['./update-platform.component.css']
})
export class UpdatePlatformComponent extends ComponentLifecycleEventEmitter implements OnInit {

    @Input()
    licenced: boolean = false;

    serverRestarting: boolean = false;
    progressPercentage: string = '';

    stderr: string = "";
    stdout: string = "";

    hasBaseDropZoneOver: boolean = false;
    uploader: FileUploader = new FileUploader({
        url: '/peek_server.update.platform',
        isHTML5: true,
        disableMultipart: true,
        queueLimit: 1,
        method: 'POST',
        autoUpload: true,
        removeAfterUpload: false
    });

    constructor(private vortexService: VortexService,
                private balloonMsg: Ng2BalloonMsgService) {
        super();

        this.doCheckEvent.subscribe(() => this.checkProgress());
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

        this.stderr = "";
        this.stdout = "";

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
                this.balloonMsg.showError("Software Update Failed\n" + data.error);
                this.stderr = data.stderr;
                this.stdout = data.stdout;
            } else {
                this.serverRestarting = true;
                this.balloonMsg.showSuccess("Software Update Complete<br/>New version is "
                    + data.message + "<br/><br/>Server will restart");
                this.reload();
            }

        } else {
            this.progressPercentage = '';
            this.balloonMsg.showError("Software Update Failed<br/> Status : " + status);
        }

        this.uploader.removeFromQueue(fileItem);
    }


    fileOverBase(e: any): void {
        this.hasBaseDropZoneOver = e;
        // <!--[(ngModel)]="files"-->
        // <!--ngf-multiple="false"-->
        // <!--ngf-allow-dir="false"-->
        // <!--ngf-drop="upload($files, $event, $rejectedFiles)"-->
        // <!--accept="'*.tar.bz2'"-->
    }


    reload() {
        setTimeout(function () {
            this.balloonMsg.showInfo("Server is restarting");
        }, 3000);
        setTimeout(function () {
            location.reload();
        }, 8000);
    };

}
