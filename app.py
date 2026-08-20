from flask import Flask
from flask_socketio import SocketIO

from config import Config
from routes.home_routes import home_bp
from routes.room_routes import room_bp
from routes.token_routes import token_bp
from sockets.room_socket import register_room_socket_events
from extensions import db, login_manager
from routes.auth_routes import auth_bp

socketio = SocketIO(async_mode="threading")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    # Inicializar SQLAlchemy
    db.init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins="*"
    )
    from models.user import User

    app.register_blueprint(home_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(auth_bp)
    register_room_socket_events(socketio)
    # Crear las tablas temporalmente
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(
            User,
            int(user_id)
        )

    return app


app = create_app()


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,

        allow_unsafe_werkzeug=True
    )