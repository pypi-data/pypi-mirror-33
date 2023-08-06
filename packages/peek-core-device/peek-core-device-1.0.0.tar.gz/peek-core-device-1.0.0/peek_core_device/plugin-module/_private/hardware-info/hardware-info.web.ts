import {Tuple, TupleOfflineStorageService, TupleSelector,addTupleType} from "@synerty/vortexjs";


import {deviceTuplePrefix} from "@peek/peek_core_device/_private/PluginNames";
import {Md5} from "ts-md5/dist/md5";

@addTupleType
class DeviceUuidTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceUuidTuple";

    uuid: string;

    constructor() {
        super(DeviceUuidTuple.tupleName);
    }
}

export function webUuid(tupleStorage: TupleOfflineStorageService): Promise<string> {
    let tupleSelector = new TupleSelector(DeviceUuidTuple.tupleName, {});

    // We don't need a real good way of getting the UUID, Peek just assigns it a token
    let browser = navigator.userAgent.substr(0, navigator.userAgent.indexOf(' '));
    let uuid = <string> Md5.hashStr(`${browser} ${new Date().toString()}`);

    return <any> tupleStorage
        .loadTuples(tupleSelector)
        .then((tuples: DeviceUuidTuple[]) => {
            // If we have a UUID already, then use that.
            if (tuples.length != 0) {
                return tuples[0].uuid;
            }

            // Create a new tuple to store
            let newTuple = new DeviceUuidTuple();
            newTuple.uuid = uuid;

            // Store the UUID, and upon successful storage, return the generated uuid
            return tupleStorage
                .saveTuples(tupleSelector, [newTuple])
                .then(() => uuid);
        });
}
