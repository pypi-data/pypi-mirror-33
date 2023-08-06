import {Component, OnInit} from "@angular/core";
import {TitleService} from "@synerty/peek-util";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";

import {
    DeviceNavService,
    DeviceServerService,
    DeviceTupleService,
    EnrolDeviceAction,
    ServerInfoTuple
} from "@peek/peek_core_device/_private";

import {DeviceEnrolmentService, DeviceInfoTuple} from "@peek/peek_core_device";
import {DeviceTypeEnum} from "@peek/peek_core_device/_private/hardware-info/hardware-info.abstract";

import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";


@Component({
    selector: 'core-device-enroll',
    templateUrl: 'enroll.component.web.html',
    moduleId: module.id
})
export class EnrollComponent extends ComponentLifecycleEventEmitter implements OnInit {

    data: EnrolDeviceAction = new EnrolDeviceAction();

    deviceType: DeviceTypeEnum;

    constructor(private balloonMsg: Ng2BalloonMsgService,
                private titleService: TitleService,
                private tupleService: DeviceTupleService,
                private nav: DeviceNavService,
                private enrolmentService: DeviceEnrolmentService) {
        super();

        this.deviceType = this.tupleService.hardwareInfo.deviceType();

        // Make sure we're not on this page when things are fine.
        let sub = this.doCheckEvent
            .takeUntil(this.onDestroyEvent)
            .subscribe(() => {
                if (this.enrolmentService.isEnrolled()) {
                    this.nav.toHome();
                    sub.unsubscribe();
                } else if (this.enrolmentService.isSetup()) {
                    this.nav.toEnrolling();
                    sub.unsubscribe();
                }
            });

    }

    ngOnInit() {
        this.titleService.setEnabled(false);
        this.titleService.setTitle('');

        let t = this.deviceType;

        // Use DeviceInfoTuple to convert it.
        let deviceInfo = new DeviceInfoTuple();
        deviceInfo.setDeviceType(t);
        this.data.deviceType = deviceInfo.deviceType;

        this.tupleService.hardwareInfo.uuid()
            .then(uuid => this.data.deviceId = uuid);

    }

    enrollEnabled(): boolean {
        if (this.data.description == null || !this.data.description.length)
            return false;

        return true;

    }

    enrollClicked() {
        this.tupleService.tupleAction.pushAction(this.data)
            .then((tuples: DeviceInfoTuple[]) => {
                this.balloonMsg.showSuccess("Enrollement successful");
            })
            .catch((err) => {
                this.balloonMsg.showError(err);
            });

    }


}