import {Injectable} from "@angular/core";
import {ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot} from "@angular/router";
import {TitleService} from "@synerty/peek-util";
import {DeviceEnrolmentService} from "./device-enrolment.service";
import {DeviceNavService} from "./_private/device-nav.service";
import {DeviceServerService} from "./_private/device-server.service";
import {Observable} from "rxjs/Observable";

@Injectable()
export class DeviceEnrolledGuard implements CanActivate {
    constructor(private enrolmentService: DeviceEnrolmentService,
                private nav: DeviceNavService,
                private titleService: TitleService,
                private serverService: DeviceServerService) {
    }

    canActivate(route: ActivatedRouteSnapshot,
                state: RouterStateSnapshot):  Promise<boolean> | boolean {

        // If the server service is still loading, come back later
        // This only applies to when the app is initialising
        // Applyhing this to NativeScript causes it to not load at all
        if (this.serverService.isWeb && this.serverService.isLoading) {
            return new Promise((resolve) => {
                this.serverService.connInfoObserver
                    .first()
                    .subscribe(() => {
                        resolve(this.canActivate(route, state));
                    });
            });
        }

        if (!this.serverService.isSetup) {
            this.nav.toConnect();
            return false;
        }

        // If the enrolment service is still loading, the come back later
        // This only applies to when the app is initialising
        // Applyhing this to NativeScript causes it to not load at all
        if (this.serverService.isWeb && this.enrolmentService.isLoading()) {
            return new Promise((resolve) => {
                this.enrolmentService.deviceInfoObservable()
                    .first()
                    .subscribe(() => {
                        resolve(this.canActivate(route, state));
                    });
            });
        }


        if (this.enrolmentService.isEnrolled()) {
            this.titleService.setEnabled(true);
            return true;
        }

        // This will take care of navigating to where to need to go to enroll
        if (this.enrolmentService.checkEnrolment()) {
            this.titleService.setEnabled(true);
            return true;
        }

        return false;
    }
}