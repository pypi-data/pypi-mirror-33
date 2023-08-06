import {Injectable} from "@angular/core";
import {TitleService} from "@synerty/peek-util";
import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";
import {TupleSelector, VortexStatusService} from "@synerty/vortexjs";
import {DeviceInfoTuple} from "./DeviceInfoTuple";
import {DeviceNavService} from "./_private/device-nav.service";
import {DeviceTupleService} from "./_private/device-tuple.service";
import {DeviceServerService} from "./_private/device-server.service";


@Injectable()
export class DeviceEnrolmentService {

    deviceInfo: DeviceInfoTuple = null;

    // There is no point having multiple services observing the same thing
    // So lets create a nice observable for the device info.
    private deviceInfoSubject = new Subject<DeviceInfoTuple>();

    private _isLoading = true;


    constructor(private nav: DeviceNavService,
                private titleService: TitleService,
                private vortexStatusService: VortexStatusService,
                private tupleService: DeviceTupleService,
                private serverService: DeviceServerService) {

        this.tupleService.hardwareInfo.uuid()
            .then(uuid => {
                // Create the tuple selector
                let tupleSelector = new TupleSelector(
                    DeviceInfoTuple.tupleName, {
                        "deviceId": uuid
                    }
                );

                // There is no point unsubscribing this
                this.tupleService.offlineObserver
                    .subscribeToTupleSelector(tupleSelector)
                    .subscribe((tuples: DeviceInfoTuple[]) => {
                        this._isLoading = false;
                        
                        if (tuples.length == 1)
                            this.deviceInfo = tuples[0];
                        else
                            this.deviceInfo = null;

                        this.deviceInfoSubject.next(this.deviceInfo);
                        this.checkEnrolment();
                    });
            });

    }

    get serverHttpUrl(): string {
        let host = this.serverService.serverHost;
        let httpProtocol = this.serverService.serverUseSsl ? 'https' : 'http';
        let httpPort = this.serverService.serverHttpPort;

        return `${httpProtocol}://${host}:${httpPort}`;
    }

    get serverWebsocketVortexUrl(): string {
        let host = this.serverService.serverHost;
        let wsProtocol = this.serverService.serverUseSsl ? 'wss' : 'ws';
        let wsPort = this.serverService.serverWebsocketPort;

        return `${wsProtocol}://${host}:${wsPort}/vortexws`;
    }

    checkEnrolment(): boolean {

        if (!this.serverService.isSetup)
            return false;

        // Do Nothing
        if (this.deviceInfo == null) {
            console.log("Device Enrollment Has Not Started");
            this.nav.toEnroll();
            return false;
        }

        if (!this.deviceInfo.isEnrolled) {
            console.log("Device Enrollment Is Waiting Approval");
            this.nav.toEnrolling();
            return false;
        }

        return true;
    }
    
    deviceInfoObservable() : Observable<DeviceInfoTuple> {
        return this.deviceInfoSubject;
    }

    isLoading(): boolean {
        return this._isLoading;
    }

    isSetup(): boolean {
        return this.deviceInfo != null;
    }


    isEnrolled(): boolean {
        return this.deviceInfo != null && this.deviceInfo.isEnrolled;
    }

    enrolmentToken(): string | null {
        if (this.deviceInfo == null)
            return null;
        return this.deviceInfo.deviceToken;

    }

}