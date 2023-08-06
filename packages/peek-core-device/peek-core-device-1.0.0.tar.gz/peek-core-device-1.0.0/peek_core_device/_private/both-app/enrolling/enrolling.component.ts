import {Component, OnInit} from "@angular/core";
import {TitleService} from "@synerty/peek-util";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";

import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";

import {
    DeviceNavService,
    EnrolDeviceAction,
    HardwareInfo
} from "@peek/peek_core_device/_private";
import {DeviceEnrolmentService} from "@peek/peek_core_device";


@Component({
    selector: 'core-device-enrolling',
    templateUrl: 'enrolling.component.web.html',
    moduleId: module.id
})
export class EnrollingComponent extends ComponentLifecycleEventEmitter  implements OnInit{
    data: EnrolDeviceAction = new EnrolDeviceAction();
    private hardwareInfo: HardwareInfo;

    constructor(private balloonMsg: Ng2BalloonMsgService,
                private titleService: TitleService,
                private nav: DeviceNavService,
                private enrolmentService: DeviceEnrolmentService) {
        super();

        // Make sure we're not on this page when things are fine.
        let sub  = this.doCheckEvent
            .takeUntil(this.onDestroyEvent)
            .subscribe(() => {
                if (this.enrolmentService.isEnrolled()) {
                    this.nav.toHome();
                    sub.unsubscribe();
                } else if (!this.enrolmentService.isSetup()) {
                    this.nav.toEnroll();
                    sub.unsubscribe();
                }
            });

    }

    ngOnInit() {
        this.titleService.setEnabled(false);
        this.titleService.setTitle('');
    }


}