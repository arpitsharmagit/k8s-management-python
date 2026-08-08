"""Flask Admin UI — Application factory and configuration."""
from __future__ import annotations

import logging
import os

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from app.config import settings

login_manager = LoginManager()
csrf = CSRFProtect()


class AdminUser:
    """Minimal Flask-Login user object backed by a JWT session."""

    def __init__(self, username: str, role: str, token: str) -> None:
        self.id = username
        self.username = username
        self.role = role
        self.token = token
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self) -> str:
        return self.id


# In-memory session store keyed by username
_active_sessions: dict[str, AdminUser] = {}


@login_manager.user_loader
def load_user(user_id: str) -> AdminUser | None:
    return _active_sessions.get(user_id)


def store_user(user: AdminUser) -> None:
    _active_sessions[user.id] = user


def remove_user(user_id: str) -> None:
    _active_sessions.pop(user_id, None)


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = settings.FLASK_SECRET_KEY

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    csrf.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app
