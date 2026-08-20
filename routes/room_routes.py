from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    current_app
)

from services import room_service

room_bp = Blueprint("room", __name__)


@room_bp.route("/room/<room_code>")
def room(room_code):
    username = session.get("username")
    session_room = session.get("room")
    member_id = session.get("member_id")

    if not username or not session_room:
        return redirect(url_for("home.index"))

    if room_code != session_room:
        return redirect(url_for("home.index"))

    current_room = room_service.get_room(room_code)

    if current_room is None:
        return redirect(url_for("home.index"))

    member = None

    if member_id:
        member = current_room.members.get(member_id)

        if member is None:
            member = current_room.waiting_members.get(member_id)

    # Solo crea un participante si realmente no existe.
    if member is None:
        member = room_service.add_member(
            room_code,
            username
        )

    if member is None:
        return redirect(url_for("home.index"))

    session["member_id"] = member.id

    if not member.approved:
        return render_template(
            "waiting_room.html",
            username=username,
            room_code=room_code
        )

    is_host = member.id == current_room.host.id

    return render_template(
        "room.html",
        username=username,
        room_code=room_code,
        members=room_service.get_members(room_code),
        waiting_members=room_service.get_waiting_members(
            room_code
        ),
        messages=room_service.get_messages(room_code),
        livekit_url=current_app.config["LIVEKIT_URL"],
        is_host=is_host
    )

@room_bp.route(
    "/room/<room_code>/host/tables"
)
def host_tables(room_code):
    session_room = session.get("room")
    member_id = session.get("member_id")

    if not session_room or not member_id:
        return redirect(
            url_for("home.index")
        )

    if session_room != room_code:
        return redirect(
            url_for("home.index")
        )

    current_room = room_service.get_room(
        room_code
    )

    if current_room is None:
        return redirect(
            url_for("home.index")
        )

    if current_room.host.id != member_id:
        return redirect(
            url_for(
                "room.room",
                room_code=room_code
            )
        )

    return render_template(
        "host_tables.html",
        room_code=room_code,
        tables=current_room.get_state()["tables"]
    )

@room_bp.route(
    "/room/<room_code>/table/<table_id>"
)
def table_room(
    room_code,
    table_id
):
    session_room = session.get("room")
    member_id = session.get("member_id")

    if not session_room or not member_id:
        return redirect(
            url_for("home.index")
        )

    if session_room != room_code:
        return redirect(
            url_for("home.index")
        )

    current_room = room_service.get_room(
        room_code
    )

    if current_room is None:
        return redirect(
            url_for("home.index")
        )

    table = current_room.tables.get(
        table_id
    )

    if table is None:
        return redirect(
            url_for(
                "room.room",
                room_code=room_code
            )
        )

    member = current_room.members.get(
        member_id
    )

    if member is None:
        return redirect(
            url_for("home.index")
        )

    is_host = member.id == current_room.host.id

    if not is_host and member.table_id != table_id:
        return redirect(
            url_for(
                "room.room",
                room_code=room_code
            )
        )

    return render_template(
        "table_room.html",
        username=member.username,
        room_code=room_code,
        table=table,
        is_host=is_host,
        livekit_url=current_app.config[
            "LIVEKIT_URL"
        ]
    )