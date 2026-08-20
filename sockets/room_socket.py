from flask import request, session
from flask_socketio import (
    emit,
    join_room,
    leave_room,
    send
)

from services import room_service


def register_room_socket_events(socketio):
    connected_sockets = {}
    def serialize_member(member):
        return {
            "id": member.id,
            "username": member.username,
            "role": member.role,
            "table_id": member.table_id,
            "connected": member.socket_id is not None
        }

    def emit_room_state(room_code):
        room = room_service.get_room(room_code)

        if room is None:
            return

        active_members = [
            serialize_member(member)
            for member in room.members.values()
            if member.socket_id is not None
        ]

        waiting_members = [
            serialize_member(member)
            for member in room.waiting_members.values()
            if member.socket_id is not None
        ]

        socketio.emit(
            "update_members",
            {
                "members": active_members
            },
            to=room_code
        )

        socketio.emit(
            "update_waiting_members",
            {
                "members": waiting_members
            },
            to=room_code
        )

    @socketio.on("start_tables")
    def handle_start_tables(data):
        room_code = session.get("room")
        member_id = session.get("member_id")

        if not room_code or not member_id:
            emit(
                "tables_error",
                {
                    "message": "Invalid room session"
                }
            )
            return

        room = room_service.get_room(room_code)

        if room is None:
            emit(
                "tables_error",
                {
                    "message": "Room does not exist"
                }
            )
            return

        if room.host.id != member_id:
            emit(
                "tables_error",
                {
                    "message": "Only the host can create tables"
                }
            )
            return

        try:
            members_per_table = int(
                data.get("members_per_table", 4)
            )
        except (TypeError, ValueError):
            emit(
                "tables_error",
                {
                    "message": "Invalid members per table value"
                }
            )
            return

        if members_per_table < 2:
            emit(
                "tables_error",
                {
                    "message": "Each table must have at least 2 members"
                }
            )
            return

        try:
            room.start_tables(
                members_per_table=members_per_table
            )
        except ValueError as error:
            emit(
                "tables_error",
                {
                    "message": str(error)
                }
            )
            return

        # Enviar al host a su panel de mesas.
        if room.host.socket_id:
            socketio.emit(
                "host_tables_ready",
                {
                    "redirect_url":
                        f"/room/{room_code}/host/tables"
                },
                to=room.host.socket_id
            )

        # Enviar a cada participante a su mesa asignada.
        for member in room.members.values():
            if member.id == room.host.id:
                continue

            if not member.approved:
                continue

            if not member.table_id:
                continue

            if not member.socket_id:
                continue

            socketio.emit(
                "table_assigned",
                {
                    "table_id": member.table_id,
                    "redirect_url":
                        f"/room/{room_code}/table/{member.table_id}"
                },
                to=member.socket_id
            )
    @socketio.on("connect")
    def handle_connect():
        room_code = session.get("room")
        username = session.get("username")
        member_id = session.get("member_id")

        if not room_code or not username or not member_id:
            return False

        room = room_service.get_room(room_code)

        if room is None:
            return False

        member = room.members.get(member_id)

        if member is None:
            member = room.waiting_members.get(member_id)

        if member is None:
            return False

        member.socket_id = request.sid

        connected_sockets[request.sid] = {
            "room_code": room_code,
            "member_id": member_id
        }

        join_room(room_code)

        emit_room_state(room_code)


    @socketio.on("message")
    def handle_message(data):
        room_code = session.get("room")
        username = session.get("username")
        member_id = session.get("member_id")

        if not room_code or not username or not member_id:
            return

        room = room_service.get_room(room_code)

        if room is None:
            return

        if member_id not in room.members:
            return

        message = data.get("message", "").strip()

        if not message:
            return

        room_service.add_message(
            room_code,
            username,
            message
        )

        send(
            {
                "name": username,
                "message": message
            },
            to=room_code
        )

    @socketio.on("disconnect")
    def handle_disconnect():
        connection = connected_sockets.pop(
            request.sid,
            None
        )

        if connection is None:
            return

        room_code = connection["room_code"]
        member_id = connection["member_id"]

        room = room_service.get_room(room_code)

        if room is None:
            return

        member = room.members.get(member_id)

        if member is None:
            member = room.waiting_members.get(member_id)

        if member is not None:
            member.socket_id = None

        leave_room(room_code)

        emit_room_state(room_code)

    @socketio.on("approve_member")
    def handle_approve_member(data):
        room_code = session.get("room")
        host_id = session.get("member_id")
        member_id = data.get("member_id")

        if not room_code or not host_id or not member_id:
            return

        room = room_service.get_room(room_code)

        if room is None:
            return

        if room.host.id != host_id:
            emit(
                "approval_error",
                {
                    "message": "Only the host can approve members"
                }
            )
            return

        member = room_service.approve_member(
            room_code,
            member_id
        )

        if member is None:
            emit(
                "approval_error",
                {
                    "message": "Member could not be approved"
                }
            )
            return

        if member.socket_id:
            emit(
                "member_approved",
                {
                    "room_code": room_code
                },
                to=member.socket_id
            )

        emit_room_state(room_code)

    @socketio.on("reject_member")
    def handle_reject_member(data):
        room_code = session.get("room")
        host_id = session.get("member_id")
        member_id = data.get("member_id")

        if not room_code or not host_id or not member_id:
            return

        room = room_service.get_room(room_code)

        if room is None:
            return

        if room.host.id != host_id:
            emit(
                "approval_error",
                {
                    "message": "Only the host can reject members"
                }
            )
            return

        waiting_member = room.waiting_members.get(member_id)

        if waiting_member is None:
            return

        socket_id = waiting_member.socket_id

        rejected_member = room_service.reject_member(
            room_code,
            member_id
        )

        if rejected_member is None:
            return

        if socket_id:
            emit(
                "member_rejected",
                {
                    "message": "Your request was rejected"
                },
                to=socket_id
            )

        emit_room_state(room_code)

    @socketio.on("leave_room_app")
    def handle_leave_room_app():
        room_code = session.get("room")
        member_id = session.get("member_id")

        if not room_code or not member_id:
            return

        room = room_service.get_room(room_code)

        if room is None:
            return

        member = room.members.get(member_id)

        if member is not None:
            if member.id != room.host.id:
                room_service.remove_member(
                    room_code,
                    member_id
                )
            else:
                member.socket_id = None

        room.waiting_members.pop(member_id, None)

        leave_room(room_code)

        emit_room_state(room_code)

        session.pop("member_id", None)
        session.pop("username", None)
        session.pop("room", None)

        emit("left_room")