import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {RouterModule, Routes} from "@angular/router";
import {EditSettingComponent} from "./edit-setting-table/edit.component";
import {FileUploadModule} from "ng2-file-upload";
// Import the required classes from VortexJS
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleDataOfflineObserverService
} from "@synerty/vortexjs";
// Import our components
import {DeviceComponent} from "./device.component";
import {DeviceUpdateComponent} from "./device-update-table/device-update.component";
import {DeviceInfoComponent} from "./device-info-table/device-info.component";
import {
    deviceActionProcessorName,
    deviceFilt,
    deviceObservableName,
    deviceTupleOfflineServiceName
} from "@peek/peek_core_device/_private";
import {UploadDeviceUpdateComponent} from "./upload-device-update/upload-device-update.component";


export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        deviceActionProcessorName, deviceFilt);
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        deviceObservableName, deviceFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(deviceTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: '',
        component: DeviceComponent
    }

];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        FileUploadModule],
    exports: [],
    providers: [
        TupleActionPushService, {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory
        },
        TupleOfflineStorageService, {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory
        },
        TupleDataObserverService, TupleDataOfflineObserverService, {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory
        },
    ],
    declarations: [
        DeviceComponent, DeviceInfoComponent, DeviceUpdateComponent,
        UploadDeviceUpdateComponent, EditSettingComponent
    ]
})
export class DeviceModule {

}