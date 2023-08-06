import {Component, OnInit} from "@angular/core";
import {
  ComponentLifecycleEventEmitter,
  Payload,
  PayloadEnvelope,
  Tuple,
  TupleLoader,
  VortexService
} from "@synerty/vortexjs";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";

@Component({
  selector: 'app-update-license',
  templateUrl: './update-license.component.html',
  styleUrls: ['./update-license.component.css']
})
export class UpdateLicenseComponent extends ComponentLifecycleEventEmitter implements OnInit {
  private readonly filt = {
    plugin: "peek_server",
    key: "admin.capabilities.data"
  };

  data: {} = {};
  private loader: TupleLoader;

  // @Output("licenced")
  // licencedOutput : EventEmitter<boolean> = new EventEmitter<boolean>();
  licenced: boolean = false;

  constructor(private vortexService: VortexService,
              private balloonMsg: Ng2BalloonMsgService) {
    super();

    vortexService.createEndpointObservable(this, this.filt)
      .subscribe((payloadEnvelope: PayloadEnvelope) =>
        this.processPayload(payloadEnvelope)
      );

    // Trigger the server to send the latest data
    vortexService.sendFilt(this.filt);
  }

  ngOnInit() {
  }

  private processPayload(payloadEnvelope: PayloadEnvelope): void {
    // if (payloadEnvelope.result) {
    //   if (payloadEnvelope.result["success"])
    //     this.balloonMsg.showSuccess(payloadEnvelope.result["message"]);
    //   else
    //     this.balloonMsg.showError(payloadEnvelope.result["message"]);
    // }
    //
    // if (payload.tuples.length) {
    //   this.data = payload.tuples[0].data;
    //   this.licenced = !(this.data["supportExceeded"]
    //     && !this.data["demoExceeded"]);
    // }
  }

  updateLicense() {
    let dataWrapTuple = new Tuple('c.s.r.datawraptuple');
    dataWrapTuple["data"] = this.data["newkey"];
    this.vortexService.sendTuple(this.filt, [dataWrapTuple]);
  }
}
