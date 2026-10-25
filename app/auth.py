from flask import Blueprint, flash, get_flashed_messages, redirect, render_template, request, session, url_for
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from database import engine
from .models import User


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        with Session(engine) as database_session:
            user = database_session.query(User).filter_by(email=email).first()

            if user and check_password_hash(user.password_hash, password):
                if user.status != "Active":
                    flash("This account is inactive.")
                    return redirect(url_for("auth.login"))

                if user.role == "Trek Staff":
                    if user.staff_profile is None or user.staff_profile.status != "Active":
                        flash("This staff account is inactive.")
                        return redirect(url_for("auth.login"))

                if user.role in ["Admin", "Trek Staff", "Trekker"]:
                    session.clear()
                    session["user_id"] = user.user_id
                    session["user_name"] = user.name
                    session["role"] = user.role

                    if user.role == "Admin":
                        return redirect(url_for("main.admin_dashboard"))
                    elif user.role == "Trek Staff":
                        return redirect(url_for("main.staff_dashboard"))
                    else:
                        return redirect(url_for("main.trekker_dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("auth.login"))

    messages = get_flashed_messages()
    message = messages[0] if messages else ""
    return render_template("login.html", message=message)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        with Session(engine) as database_session:
            existing_user = database_session.query(User).filter_by(email=email).first()

            if existing_user:
                flash("An account with this email already exists.")
                return redirect(url_for("auth.register"))

            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                role="Trekker",
            )
            database_session.add(user)
            database_session.commit()

        flash("Registration complete. Please log in.")
        return redirect(url_for("auth.login"))

    messages = get_flashed_messages()
    message = messages[0] if messages else ""
    return render_template("register.html", message=message)


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
