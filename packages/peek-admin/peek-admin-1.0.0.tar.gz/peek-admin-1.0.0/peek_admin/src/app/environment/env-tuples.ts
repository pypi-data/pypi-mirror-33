import {Tuple} from "@synerty/vortexjs";

export class PeekEnvServer extends Tuple {
    constructor() {
        super("peek_server.env.server");
    }

    id: number;
    name: string;
    description: string;
    ip: string;

}


export class PeekEnvWorker extends Tuple {
    constructor() {
        super("peek_server.env.worker");
    }

    id: number;
    name: string;
    description: string;
    ip: string;
    serverId: number;
}

export class PeekEnvAgent extends Tuple {
    constructor() {
        super("peek_server.env.agent");
    }

    id: number;
    name: string;
    description: string;
    ip: string;
    serverId: number;
}

export class PeekEnvClient extends Tuple {
    constructor() {
        super("peek_server.env.client");
    }

    id: number;
    name: string;
    description: string;
    ip: string;
    serverId: number;
}