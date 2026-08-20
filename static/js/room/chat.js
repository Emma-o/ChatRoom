import {
    registerWaitingRoomEvents
} from "./waiting_requests.js";


export function initializeChat(
    socket,
    username
) {
    registerWaitingRoomEvents(socket);

    const messages =
        document.getElementById("messages");

    const messageInput =
        document.getElementById("message");

    const sendButton =
        document.getElementById("send-btn");

    socket.on("message", (data) => {
        createMessage(
            data.name,
            data.message,
            username,
            messages
        );
    });

    socket.on("update_members", (data) => {
        updateMembers(data.members);
    });

    function sendMessage() {
        const message = messageInput.value.trim();

        if (!message) {
            messageInput.value = "";
            return;
        }

        socket.emit("message", {
            message
        });

        messageInput.value = "";
    }

    sendButton.addEventListener(
        "click",
        sendMessage
    );

    messageInput.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                sendMessage();
            }
        }
    );
}


function createMessage(
    name,
    message,
    currentUsername,
    messagesContainer
) {
    const isMine = name === currentUsername;

    const container =
        document.createElement("div");

    container.className =
        `text ${isMine ? "mine" : ""}`;

    const textContainer =
        document.createElement("span");

    const nameElement =
        document.createElement("strong");

    nameElement.textContent = `${name}: `;

    textContainer.appendChild(nameElement);

    textContainer.appendChild(
        document.createTextNode(message)
    );

    const date =
        document.createElement("span");

    date.className = "muted";

    date.textContent =
        new Date().toLocaleString();

    container.appendChild(textContainer);
    container.appendChild(date);

    messagesContainer.appendChild(container);

    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;
}



function updateMembers(members) {
    const participantsList =
        document.getElementById("participants-list");

    const memberCount =
        document.getElementById("member-count");

    participantsList.innerHTML = "";

    members.forEach((member) => {
        const participant =
            document.createElement("div");

        participant.classList.add("participant-item");

        participant.innerHTML = `
            <span class="online-dot"></span>
            <span>${member.username}</span>
        `;

        participantsList.appendChild(participant);
    });

    memberCount.textContent = members.length;
}