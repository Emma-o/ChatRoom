from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from flask_login import (
    current_user,
    login_required
)
from services import room_service

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template(
            "index.html"
        )

    username = current_user.username

    code = request.form.get(
        "code",
        ""
    ).strip().upper()

    create_button = request.form.get(
        "btncreate"
    )

    join_button = request.form.get(
        "btnjoin"
    )

    if join_button is not None:
        if not code:
            return render_template(
                "index.html",
                error="Please enter a room code",
                code=code
            )

        if not room_service.room_exists(code):
            return render_template(
                "index.html",
                error="Room doesn't exist",
                code=code
            )

    if create_button is not None:
        if current_user.role != "host":
            abort(403)

        room = room_service.create_room(
            username
        )

        code = room.code

        session["member_id"] = room.host.id

    session["username"] = username
    session["room"] = code

    return redirect(
        url_for(
            "room.room",
            room_code=code
        )
    )