import {Component, OnInit} from '@angular/core';


import {VortexService} from "@synerty/vortexjs";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  constructor(private vortexService: VortexService) {

  }

  ngOnInit() {
    this.vortexService.reconnect();
  }


}
