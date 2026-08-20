import {
    initializeChat
} from "./chat.js";

import {
    initializeTables
} from "./tables.js";


const config = window.roomConfig;

if (!config) {
    throw new Error(
        "window.roomConfig is not defined"
    );
}

const socket = io({
    transports: ["websocket"],
    upgrade: false
});

initializeChat(
    socket,
    config.username
);

initializeTables(socket);