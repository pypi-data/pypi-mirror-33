import {addTupleType, Tuple} from "@synerty/vortexjs";
import {deviceTuplePrefix} from "./_private/PluginNames";
import {DeviceTypeEnum} from "./_private/hardware-info/hardware-info.abstract";


@addTupleType
export class DeviceInfoTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceInfoTuple";

    readonly TYPE_MOBILE_IOS = "mobile-ios";
    readonly TYPE_MOBILE_ANDROUD = "mobile-android";
    readonly TYPE_MOBILE_WEB = "mobile-web";
    readonly TYPE_DESKTOP_WEB = "desktop-web";
    readonly TYPE_DESKTOP_WINDOWS = "desktop-windows";
    readonly TYPE_DESKTOP_MACOS = "desktop-macos";

    id: number;
    description: string;
    deviceId: string;
    deviceType: string;
    deviceToken: string;
    appVersion: string;
    updateVersion: string;
    lastOnline: Date;
    lastUpdateCheck:Date;
    createdDate : Date;
    isOnline: boolean;
    isEnrolled: boolean;

    setDeviceType(val:DeviceTypeEnum ) {
        switch(val) {
            case DeviceTypeEnum.DESKTOP_WEB:
                this.deviceType = this.TYPE_DESKTOP_WEB;
                break;

            case DeviceTypeEnum.DESKTOP_MACOS:
                this.deviceType = this.TYPE_DESKTOP_MACOS;
                break;

            case DeviceTypeEnum.DESKTOP_WINDOWS:
                this.deviceType = this.TYPE_DESKTOP_WINDOWS;
                break;

            case DeviceTypeEnum.MOBILE_IOS:
                this.deviceType = this.TYPE_MOBILE_IOS;
                break;

            case DeviceTypeEnum.MOBILE_ANDROID:
                this.deviceType = this.TYPE_MOBILE_ANDROUD;
                break;

            case DeviceTypeEnum.MOBILE_WEB:
                this.deviceType = this.TYPE_MOBILE_WEB;
                break;

        }
    }

    constructor() {
        super(DeviceInfoTuple.tupleName)
    }
}