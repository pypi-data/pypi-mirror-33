import {addTupleType, Tuple} from "@synerty/vortexjs";
import {deviceTuplePrefix} from "../PluginNames";


/** Web Client Vortex Details Tuple

This tuple is sent as the first tuple on every http vortex connection from the client.

It provides the client with the websocket vortex details.

*/
@addTupleType
export class WebClientVortexDetailsTuple extends Tuple {

    public static readonly tupleName = deviceTuplePrefix + "WebClientVortexDetailsTuple";

    useSsl: boolean;
    httpPort: number;
    websocketPort: number;
    host: string;

    constructor() {
        super(WebClientVortexDetailsTuple.tupleName)
    }

}