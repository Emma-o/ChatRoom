export function registerWaitingRoomEvents(socket) {
    const waitingContainer = document.getElementById(
        "waiting-members"
    );

    if (!waitingContainer) {
        return;
    }

    waitingContainer.addEventListener("click", (event) => {
        const button = event.target.closest("button");

        if (!button) {
            return;
        }

        const memberId = button.dataset.memberId;

        if (!memberId) {
            return;
        }

        if (button.classList.contains("approve-member")) {
            socket.emit("approve_member", {
                member_id: memberId
            });
        }

        if (button.classList.contains("reject-member")) {
            socket.emit("reject_member", {
                member_id: memberId
            });
        }
    });

    socket.on("update_waiting_members", (data) => {
        renderWaitingMembers(
            waitingContainer,
            data.members || []
        );
    });

    socket.on("approval_error", (data) => {
        console.error(data.message);
    });
}


function renderWaitingMembers(container, members) {
    container.innerHTML = "";

    if (members.length === 0) {
        const message = document.createElement("p");
        message.className = "no-waiting-members";
        message.textContent = "No pending requests";

        container.appendChild(message);
        return;
    }

    members.forEach((member) => {
        const row = document.createElement("div");
        row.className = "waiting-member";
        row.dataset.memberId = member.id;

        const username = document.createElement("span");
        username.textContent = member.username;

        const approveButton = document.createElement("button");
        approveButton.type = "button";
        approveButton.className = "approve-member";
        approveButton.dataset.memberId = member.id;
        approveButton.textContent = "Approve";

        const rejectButton = document.createElement("button");
        rejectButton.type = "button";
        rejectButton.className = "reject-member";
        rejectButton.dataset.memberId = member.id;
        rejectButton.textContent = "Reject";

        row.append(
            username,
            approveButton,
            rejectButton
        );

        container.appendChild(row);
    });
}