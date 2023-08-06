import {Injectable} from "@angular/core";
import {DeviceUpdateTuple} from "./tuples/DeviceUpdateTuple";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {DeviceServerService} from "./device-server.service";


@Injectable()
export class DeviceUpdateServiceDelegate {

    constructor(private serverService:DeviceServerService,
                private balloonMsg: Ng2BalloonMsgService) {
    }

    get updateInProgress():boolean {
        return false;
    }

    updateTo(deviceUpdate: DeviceUpdateTuple) :Promise<void>{
        return Promise.resolve();
    }

}