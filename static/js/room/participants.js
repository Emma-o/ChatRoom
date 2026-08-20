export function createParticipantCard(participant, videoArea) {
    let card = document.querySelector(
        `.video-card[data-participant="${participant.identity}"]`
    );

    if (card) {
        return card;
    }

    card = document.createElement("div");
    card.className = "video-card";
    card.dataset.participant = participant.identity;

    const avatar = document.createElement("div");
    avatar.className = "participant-avatar";

    const avatarCircle = document.createElement("div");
    avatarCircle.className = "avatar-circle";

    const displayName =
        participant.name || participant.identity;

    avatarCircle.textContent =
        displayName.charAt(0).toUpperCase();

    const nameLabel = document.createElement("div");
    nameLabel.className = "participant-name";
    nameLabel.textContent = displayName;

    avatar.appendChild(avatarCircle);

    card.appendChild(avatar);
    card.appendChild(nameLabel);

    videoArea.appendChild(card);

    return card;
}


export function setParticipantCameraState(
    participantIdentity,
    cameraEnabled
) {
    const card = document.querySelector(
        `.video-card[data-participant="${participantIdentity}"]`
    );

    if (!card) {
        return;
    }

    const avatar = card.querySelector(".participant-avatar");
    const video = card.querySelector("video");

    if (cameraEnabled) {
        if (avatar) {
            avatar.style.display = "none";
        }

        if (video) {
            video.style.display = "block";
        }
    } else {
        if (video) {
            video.style.display = "none";
        }

        if (avatar) {
            avatar.style.display = "flex";
        }
    }
}


export function removeParticipantCard(participantIdentity) {
    const card = document.querySelector(
        `.video-card[data-participant="${participantIdentity}"]`
    );

    if (card) {
        card.remove();
    }
}


export function attachVideoTrack(
    track,
    participant,
    videoArea,
    muted = false
) {
    const card = createParticipantCard(
        participant,
        videoArea
    );

    const previousVideo = card.querySelector("video");

    if (previousVideo) {
        previousVideo.remove();
    }

    const videoElement = track.attach();

    videoElement.playsInline = true;
    videoElement.muted = muted;
    videoElement.dataset.participant =
        participant.identity;

    card.insertBefore(
        videoElement,
        card.querySelector(".participant-name")
    );

    return videoElement;
}