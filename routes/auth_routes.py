from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    current_user,
    login_user,
    logout_user
)

from extensions import db
from models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():
    if request.method == "GET":
        return render_template(
            "auth/register.html"
        )

    username = request.form.get(
        "username",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    role = request.form.get(
        "role",
        "participant"
    )

    if not username or not email or not password:
        return render_template(
            "auth/register.html",
            error="All fields are required."
        )

    if role not in {"host", "participant"}:
        role = "participant"

    existing_user = db.session.execute(
        db.select(User).where(
            (User.username == username)
            | (User.email == email)
        )
    ).scalar_one_or_none()

    if existing_user is not None:
        return render_template(
            "auth/register.html",
            error="Username or email already exists."
        )

    user = User(
        username=username,
        email=email,
        role=role
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    login_user(user)

    return redirect(
        url_for("home.index")
    )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():
    if current_user.is_authenticated:
        return redirect(
            url_for("home.index")
        )

    if request.method == "GET":
        return render_template(
            "auth/login.html"
        )

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    if not email or not password:
        return render_template(
            "auth/login.html",
            error="Email and password are required."
        )

    user = db.session.execute(
        db.select(User).where(
            User.email == email
        )
    ).scalar_one_or_none()

    if user is None:
        return render_template(
            "auth/login.html",
            error="Invalid email or password."
        )

    if not user.check_password(password):
        return render_template(
            "auth/login.html",
            error="Invalid email or password."
        )

    login_user(user)

    return redirect(
        url_for("home.index")
    )


@auth_bp.route("/logout")
def logout():
    logout_user()

    return redirect(
        url_for("auth.login")
    )