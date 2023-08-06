import {Tuple, TupleOfflineStorageService, TupleSelector,addTupleType} from "@synerty/vortexjs";



export enum DeviceTypeEnum {
    MOBILE_WEB,
    MOBILE_IOS,
    MOBILE_ANDROID,
    DESKTOP_WEB,
    DESKTOP_WINDOWS,
    DESKTOP_MACOS
}


export interface HardwareInfoI {
    uuid(): Promise<string> ;
    description(): string;
    deviceType(): DeviceTypeEnum;
}