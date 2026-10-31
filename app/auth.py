from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from database import engine
from .models import User


auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/register")
def register():
    return render_template("register.html")


@auth.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data["email"].strip().lower()
    password = data["password"]

    with Session(engine) as database_session:
        user = database_session.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.status != "Active":
                return jsonify({"message": "This account is inactive."}), 403

            if user.role == "Trek Staff":
                if user.staff_profile is None or user.staff_profile.status != "Active":
                    return jsonify({"message": "This staff account is inactive."}), 403

            if user.role in ["Admin", "Trek Staff", "Trekker"]:
                session.clear()
                session["user_id"] = user.user_id
                session["user_name"] = user.name
                session["role"] = user.role

                if user.role == "Admin":
                    next_page = url_for("main.admin_dashboard")
                elif user.role == "Trek Staff":
                    next_page = url_for("main.staff_dashboard")
                else:
                    next_page = url_for("main.trekker_dashboard")
                return jsonify({"redirect": next_page})

    return jsonify({"message": "Invalid email or password."}), 401


@auth.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json()
    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    with Session(engine) as database_session:
        existing_user = database_session.query(User).filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "An account with this email already exists."}), 400

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="Trekker",
        )
        database_session.add(user)
        database_session.commit()

    return jsonify({"message": "Registration complete. Please log in."})


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
