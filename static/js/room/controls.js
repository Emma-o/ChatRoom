import {
    setParticipantCameraState
} from "./participants.js";


export function initializeControls(room,socket) {
    const micBtn = document.getElementById("mic-btn");
    const camBtn = document.getElementById("cam-btn");
    const leaveBtn = document.getElementById("leave-btn");

    let micEnabled = false;
    let camEnabled = false;

    micBtn.addEventListener("click", async () => {
        try {
            micEnabled = !micEnabled;

            await room.localParticipant
                .setMicrophoneEnabled(micEnabled);

            micBtn.textContent = micEnabled
                ? "🎙️ Mute"
                : "🔇 Unmute";
        } catch (error) {
            console.error(
                "Could not change microphone state:",
                error
            );
        }
    });

    camBtn.addEventListener("click", async () => {
        try {
            camEnabled = !camEnabled;

            await room.localParticipant
                .setCameraEnabled(camEnabled);

            setParticipantCameraState(
                room.localParticipant.identity,
                camEnabled
            );

            camBtn.textContent = camEnabled
                ? "📷 Camera Off"
                : "📷 Camera On";
        } catch (error) {
            console.error(
                "Could not change camera state:",
                error
            );
        }
    });

    leaveBtn.addEventListener("click", () => {
        socket.emit("leave_room_app");
        room.disconnect();
        window.location.href = "/";
    });

    return {
        setInitialState(
            microphoneEnabled,
            cameraEnabled
        ) {
            micEnabled = microphoneEnabled;
            camEnabled = cameraEnabled;

            micBtn.textContent = micEnabled
                ? "🎙️ Mute"
                : "🔇 Microphone On";

            camBtn.textContent = camEnabled
                ? "📷 Camera Off"
                : "📷 Camera On";
        }
    };
}