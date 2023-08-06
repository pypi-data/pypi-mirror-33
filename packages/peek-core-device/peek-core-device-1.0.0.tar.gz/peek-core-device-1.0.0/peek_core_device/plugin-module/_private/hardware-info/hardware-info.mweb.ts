import {DeviceTypeEnum, HardwareInfoI} from "./hardware-info.abstract";
import {webUuid} from "./hardware-info.web";
import {TupleOfflineStorageService} from "@synerty/vortexjs";


export class HardwareInfo implements HardwareInfoI {
    constructor( private tupleStorage: TupleOfflineStorageService) {

    }

    uuid(): Promise<string> {
        return webUuid(this.tupleStorage);
    }

    description(): string {
        return navigator.userAgent;
    }


    deviceType(): DeviceTypeEnum {
        return DeviceTypeEnum.MOBILE_WEB;
    }
}