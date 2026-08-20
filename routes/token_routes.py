from flask import (
    Blueprint,
    jsonify,
    current_app,
    session
)

from services import room_service
from services.livekit_service import LiveKitService

token_bp = Blueprint("token", __name__)

from flask import (
    Blueprint,
    jsonify,
    current_app,
    session,
    request
)

from services import room_service
from services.livekit_service import LiveKitService


token_bp = Blueprint("token", __name__)


@token_bp.route("/token")
def token():
    username = session.get("username")
    room_code = session.get("room")
    member_id = session.get("member_id")

    table_id = request.args.get(
        "table_id",
        ""
    ).strip()

    if not username or not room_code or not member_id:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    if not table_id:
        return jsonify({
            "error": "Table ID is required"
        }), 400

    room = room_service.get_room(room_code)

    if room is None:
        return jsonify({
            "error": "Room does not exist"
        }), 404

    member = room.members.get(member_id)

    if member is None:
        return jsonify({
            "error": "Member does not exist"
        }), 403

    if not member.approved:
        return jsonify({
            "error": "Member is not approved"
        }), 403

    table = room.tables.get(table_id)

    if table is None:
        return jsonify({
            "error": "Table does not exist"
        }), 404

    is_host = member.id == room.host.id

    if not is_host and member.table_id != table_id:
        return jsonify({
            "error": "You cannot join this table"
        }), 403

    livekit_room_name = (
        f"{room_code}-{table_id}"
    )

    livekit_service = LiveKitService(
        api_key=current_app.config[
            "LIVEKIT_API_KEY"
        ],
        api_secret=current_app.config[
            "LIVEKIT_API_SECRET"
        ]
    )

    token_value = livekit_service.create_token(
        username=member.username,
        room_name=livekit_room_name
    )

    return jsonify({
        "token": token_value,
        "room_name": livekit_room_name,
        "table_id": table_id
    })