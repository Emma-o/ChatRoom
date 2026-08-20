import {
    createLiveKitRoom,
    attachLocalVideo
} from "./livekit.js";

import {
    initializeControls
} from "./controls.js";


const config = window.roomConfig;

if (!config) {
    throw new Error(
        "window.roomConfig is not defined"
    );
}

const videoArea = document.getElementById(
    "video-area"
);

const socket = io({
    transports: ["websocket"],
    upgrade: false
});


async function startTableRoom() {
    try {
        const room = await createLiveKitRoom(
            config,
            videoArea
        );

        const controls = initializeControls(
            room,
            socket
        );

        try {
            await room.localParticipant
                .enableCameraAndMicrophone();

            controls.setInitialState(
                true,
                true
            );

            attachLocalVideo(
                room,
                videoArea
            );
        } catch (error) {
            controls.setInitialState(
                false,
                false
            );

            console.warn(
                "Camera or microphone permission denied:",
                error
            );
        }
    } catch (error) {
        console.error(
            "Could not enter the table:",
            error
        );
    }
}


startTableRoom();