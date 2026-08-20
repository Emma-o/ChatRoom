export function initializeTables(socket) {
    const startButton = document.getElementById(
        "start-tables-btn"
    );

    const membersPerTableInput = document.getElementById(
        "members-per-table"
    );

    const errorElement = document.getElementById(
        "tables-error"
    );

    socket.on("tables_created", (data) => {
        renderTables(data.tables || {});
    });

    socket.on("tables_error", (data) => {
        if (!errorElement) {
            console.error(
                data.message || "Could not create tables"
            );
            return;
        }

        errorElement.textContent =
            data.message || "Could not create tables";
    });
    socket.on("host_tables_ready", (data) => {
    if (!data.redirect_url) {
        return;
    }

    window.location.href = data.redirect_url;
});

socket.on("table_assigned", (data) => {
    if (!data.redirect_url) {
        return;
    }

    window.location.href = data.redirect_url;
});
    // Los participantes no tienen estos elementos,
    // pero sí deben recibir el evento tables_created.
    if (!startButton || !membersPerTableInput) {
        return;
    }

    startButton.addEventListener("click", () => {
        const membersPerTable = Number(
            membersPerTableInput.value
        );

        if (
            !Number.isInteger(membersPerTable)
            || membersPerTable < 2
        ) {
            if (errorElement) {
                errorElement.textContent =
                    "Enter at least 2 members per table";
            }

            return;
        }

        if (errorElement) {
            errorElement.textContent = "";
        }

        socket.emit("start_tables", {
            members_per_table: membersPerTable
        });
    });
}