import {Component, OnInit} from "@angular/core";
import {TitleService} from "@synerty/peek-util";

import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";

import {DeviceNavService, DeviceServerService} from "@peek/peek_core_device/_private";

@Component({
    selector: 'core-device-enrolling',
    templateUrl: 'connecting.component.web.html',
    moduleId: module.id
})
export class ConnectingComponent extends ComponentLifecycleEventEmitter  implements OnInit {

    constructor(private titleService: TitleService,
                private nav: DeviceNavService,
                private deviceServerService: DeviceServerService) {
        super();


        // Make sure we're not on this page when things are fine.
        let sub = this.doCheckEvent
            .takeUntil(this.onDestroyEvent)
            .subscribe(() => {
                if (this.deviceServerService.isConnected) {
                    this.nav.toEnroll();
                    sub.unsubscribe();
                } else if (!this.deviceServerService.isSetup) {
                    this.nav.toConnect();
                    sub.unsubscribe();
                }
            });

    }

    ngOnInit() {
        this.titleService.setEnabled(false);
        this.titleService.setTitle('');
    }

    reconnectClicked() {
        this.nav.toConnect();
    }

    workOfflineClicked() {
        this.deviceServerService.setWorkOffline();
    }


}