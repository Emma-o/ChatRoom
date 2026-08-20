import {
    Room,
    RoomEvent
} from "https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.esm.mjs";

import {
    createParticipantCard,
    setParticipantCameraState,
    removeParticipantCard,
    attachVideoTrack
} from "./participants.js";

export async function createLiveKitRoom(config, videoArea) {
    if (!config.tableId) {
    throw new Error(
        "The table ID is not defined"
    );
}

const tokenUrl = new URL(
    "/token",
    window.location.origin
);

tokenUrl.searchParams.set(
    "table_id",
    config.tableId
);

const response = await fetch(
    tokenUrl.toString()
);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        throw new Error(
            errorData.error ||
            "Could not obtain the LiveKit token"
        );
    }

    const data = await response.json();

    if (!data.token) {
        throw new Error(
            "The server did not return a token"
        );
    }

    const room = new Room();

    registerRoomEvents(room, videoArea);

    await room.connect(
        config.livekitUrl,
        data.token
    );

    renderExistingParticipants(
        room,
        videoArea
    );

    return room;
}


function registerRoomEvents(room, videoArea) {
    room.on(
    RoomEvent.ParticipantConnected,
    (participant) => {
        createParticipantCard(
            participant,
            videoArea
        );

        updateVideoGrid(videoArea);
    }
);

    room.on(
    RoomEvent.ParticipantDisconnected,
    (participant) => {
        removeParticipantCard(
            participant.identity
        );

        updateVideoGrid(videoArea);
    }
);

   room.on(
    RoomEvent.TrackSubscribed,
    (track, publication, participant) => {
        if (track.kind === "video") {
            attachVideoTrack(
                track,
                participant,
                videoArea
            );

            setParticipantCameraState(
                participant.identity,
                !publication.isMuted
            );

            return;
        }

        if (track.kind === "audio") {
            const audioElement = track.attach();

            audioElement.autoplay = true;
            audioElement.setAttribute(
                "data-participant",
                participant.identity
            );

            document.body.appendChild(audioElement);
        }
    }
);

    room.on(
        RoomEvent.TrackUnsubscribed,
        (track, publication, participant) => {
            track.detach().forEach((element) => {
                element.remove();
            });

            if (track.kind === "video") {
                setParticipantCameraState(
                    participant.identity,
                    false
                );
            }
        }
    );

    room.on(
        RoomEvent.TrackMuted,
        (publication, participant) => {
            if (publication.kind === "video") {
                setParticipantCameraState(
                    participant.identity,
                    false
                );
            }
        }
    );

    room.on(
        RoomEvent.TrackUnmuted,
        (publication, participant) => {
            if (publication.kind === "video") {
                setParticipantCameraState(
                    participant.identity,
                    true
                );
            }
        }
    );
}


function renderExistingParticipants(
    room,
    videoArea
) {
    createParticipantCard(
        room.localParticipant,
        videoArea
    );

    room.remoteParticipants.forEach(
        (participant) => {
            createParticipantCard(
                participant,
                videoArea
            );
        }
    );

    updateVideoGrid(videoArea);
}


export function attachLocalVideo(
    room,
    videoArea
) {
    const participant = room.localParticipant;

    const localCard = createParticipantCard(
        participant,
        videoArea
    );

    participant.videoTrackPublications.forEach(
        (publication) => {
            if (!publication.track) {
                return;
            }

            attachVideoTrack(
                publication.track,
                participant,
                videoArea,
                true
            );

            setParticipantCameraState(
                participant.identity,
                !publication.isMuted
            );
        }
    );

    updateVideoGrid(videoArea);

    return localCard;
}


export function updateVideoGrid(videoArea) {
    const participantCount =
        videoArea.querySelectorAll(".video-card").length;

    videoArea.classList.remove(
        "participants-1",
        "participants-2",
        "participants-3",
        "participants-4-plus"
    );

    videoArea.style.removeProperty(
        "--video-columns"
    );

    videoArea.style.removeProperty(
        "--video-rows"
    );

    if (participantCount === 0) {
        return;
    }

    if (participantCount <= 3) {
        videoArea.classList.add(
            `participants-${participantCount}`
        );

        return;
    }

    const columns = Math.ceil(
        Math.sqrt(participantCount)
    );

    const rows = Math.ceil(
        participantCount / columns
    );

    videoArea.classList.add(
        "participants-4-plus"
    );

    videoArea.style.setProperty(
        "--video-columns",
        columns
    );

    videoArea.style.setProperty(
        "--video-rows",
        rows
    );
}
