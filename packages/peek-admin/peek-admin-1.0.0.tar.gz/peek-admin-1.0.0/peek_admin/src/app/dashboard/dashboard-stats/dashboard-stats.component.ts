import {Component, OnInit} from "@angular/core";
import {
  VortexService,
  VortexStatusService,
  ComponentLifecycleEventEmitter,
  TupleLoader
} from "@synerty/vortexjs";

interface Stat {
  desc: string;
  value: string;
}

@Component({
  selector: 'app-dashboard-stats',
  templateUrl: './dashboard-stats.component.html',
  styleUrls: ['./dashboard-stats.component.css']
})
export class DashboardStatsComponent extends ComponentLifecycleEventEmitter implements OnInit {
  private readonly statsFilt = {
    plugin: 'peek_server',
    key: "peakadm.dashboard.list.data"
  };

  // stats: Stat[] = [];
  // loader: TupleLoader;

  constructor(vortexService: VortexService, vortexStatus: VortexStatusService) {
    super();

    // this.loader = vortexService.createTupleLoader(this, this.statsFilt);
    //
    //
    // vortexStatus
    //   .isOnline
    //   .filter(online => online)
    //   .first()
    //   .subscribe(() => {
    //     this.loader.observable.subscribe(
    //       tuples => {
    //         this.stats = <Stat[]>tuples;
    //         this.stats.sort((a, b) => {
    //           return (<Stat>a).desc.localeCompare((<Stat>b).desc);
    //         });
    //       });
    //   });

  }

  ngOnInit() {
  }

}
