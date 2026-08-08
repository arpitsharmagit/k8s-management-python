"""Flask Admin — Authentication blueprint."""
from __future__ import annotations

import logging

import requests
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length

from app import AdminUser, remove_user, store_user
from app.config import settings

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            resp = requests.post(
                f"{settings.FASTAPI_BASE_URL}/auth/token",
                json={"username": form.username.data, "password": form.password.data},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data["access_token"]

                # Decode the role from the JWT (no verification — FastAPI handles that)
                import base64, json as _json
                parts = token.split(".")
                padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
                claims = _json.loads(base64.urlsafe_b64decode(padded))
                role = claims.get("role", "viewer")

                user = AdminUser(username=form.username.data, role=role, token=token)
                store_user(user)
                login_user(user, remember=False)
                flash("Logged in successfully.", "success")
                return redirect(url_for("dashboard.index"))
            else:
                flash("Invalid credentials. Please try again.", "danger")
        except requests.exceptions.ConnectionError:
            flash("Cannot reach the API gateway. Please check connectivity.", "danger")
        except Exception as exc:
            logger.error("Login error: %s", exc)
            flash("An unexpected error occurred.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    remove_user(request.cookies.get("user_id", ""))
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
