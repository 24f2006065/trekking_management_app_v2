from datetime import date

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from werkzeug.security import generate_password_hash

from database import engine
from .models import Booking, StaffProfile, Trek, User


main = Blueprint("main", __name__)


@main.route("/")
def index():
    if session.get("role") == "Admin":
        return redirect(url_for("main.admin_dashboard"))
    elif session.get("role") == "Trek Staff":
        return redirect(url_for("main.staff_dashboard"))
    elif session.get("role") == "Trekker":
        return redirect(url_for("main.trekker_dashboard"))
    return redirect(url_for("auth.login"))


@main.route("/api/current-user")
def current_user():
    if not session.get("user_id"):
        return jsonify({"message": "Please log in."}), 401
    return jsonify({"name": session.get("user_name")})


@main.route("/admin", defaults={"page": "dashboard"})
@main.route("/admin/<page>")
def admin_dashboard(page):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") != "Admin":
        return "Unauthorized", 403

    page_templates = {
        "dashboard": "admin_dashboard.html",
        "add-trek": "admin_add_trek.html",
        "treks": "admin_manage_treks.html",
        "add-staff": "admin_add_staff.html",
        "staff": "admin_manage_staff.html",
        "users": "admin_manage_users.html",
        "bookings": "admin_bookings.html",
        "statistics": "admin_statistics.html",
    }
    template = page_templates.get(page, "admin_dashboard.html")
    return render_template(template)


@main.route("/api/admin/<page>")
def admin_data(page):
    if not session.get("user_id"):
        return jsonify({"message": "Please log in."}), 401
    if session.get("role") != "Admin":
        return jsonify({"message": "Unauthorized."}), 403

    search = request.args.get("search", "").strip()
    with Session(engine) as database_session:
        if page == "dashboard":
            counts = {
                "treks": database_session.query(Trek).count(),
                "users": database_session.query(User).filter_by(role="Trekker").count(),
                "staff": database_session.query(StaffProfile).count(),
                "bookings": database_session.query(Booking).count(),
            }
            return jsonify(counts)

        if page == "treks":
            treks_query = database_session.query(Trek)
            if search:
                if search.isdigit():
                    treks_query = treks_query.filter(
                        or_(Trek.trek_name.ilike(f"%{search}%"), Trek.trek_id == int(search))
                    )
                else:
                    treks_query = treks_query.filter(Trek.trek_name.ilike(f"%{search}%"))
            treks = treks_query.order_by(Trek.trek_id).all()
            staff = database_session.query(StaffProfile).options(
                joinedload(StaffProfile.user)
            ).join(StaffProfile.user).filter(
                User.status == "Active", StaffProfile.status == "Active"
            ).all()
            return jsonify({
                "treks": [{
                    "trek_id": trek.trek_id,
                    "trek_name": trek.trek_name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "available_slots": trek.available_slots,
                    "assigned_staff_id": trek.assigned_staff_id,
                    "status": trek.status,
                    "start_date": trek.start_date.isoformat() if trek.start_date else "",
                    "end_date": trek.end_date.isoformat() if trek.end_date else "",
                } for trek in treks],
                "staff": [{"staff_id": staff_member.staff_id, "name": staff_member.user.name} for staff_member in staff],
            })

        if page == "staff":
            staff_query = database_session.query(StaffProfile).options(
                joinedload(StaffProfile.user)
            ).join(StaffProfile.user)
            if search:
                if search.isdigit():
                    staff_query = staff_query.filter(
                        or_(User.name.ilike(f"%{search}%"), StaffProfile.staff_id == int(search))
                    )
                else:
                    staff_query = staff_query.filter(User.name.ilike(f"%{search}%"))
            staff = staff_query.order_by(StaffProfile.staff_id).all()
            return jsonify({"staff": [{
                "staff_id": staff_member.staff_id,
                "user_id": staff_member.user.user_id,
                "name": staff_member.user.name,
                "email": staff_member.user.email,
                "contact_details": staff_member.contact_details or "",
                "status": staff_member.status,
            } for staff_member in staff]})

        if page == "users":
            users_query = database_session.query(User).filter(User.role == "Trekker")
            if search:
                if search.isdigit():
                    users_query = users_query.filter(
                        or_(User.name.ilike(f"%{search}%"), User.user_id == int(search))
                    )
                else:
                    users_query = users_query.filter(User.name.ilike(f"%{search}%"))
            users = users_query.order_by(User.user_id).all()
            return jsonify({"users": [{
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "status": user.status,
            } for user in users]})

        if page == "bookings":
            bookings = database_session.query(Booking).options(
                joinedload(Booking.user), joinedload(Booking.trek)
            ).order_by(Booking.booking_date.desc()).all()
            return jsonify({"bookings": [{
                "booking_id": booking.booking_id,
                "user_name": booking.user.name,
                "trek_name": booking.trek.trek_name,
                "booking_date": booking.booking_date.isoformat(),
                "status": booking.status,
                "payment_status": booking.payment_status or "N/A",
            } for booking in bookings]})

        if page == "statistics":
            treks = database_session.query(Trek).order_by(Trek.trek_id).all()
            return jsonify({"treks": [{
                "trek_name": trek.trek_name,
                "status": trek.status,
                "booking_count": database_session.query(Booking).filter_by(trek_id=trek.trek_id).count(),
            } for trek in treks]})

    return jsonify({"message": "Page not found."}), 404


@main.route("/api/admin/actions", methods=["POST"])
def admin_actions():
    if not session.get("user_id"):
        return jsonify({"message": "Please log in."}), 401
    if session.get("role") != "Admin":
        return jsonify({"message": "Unauthorized."}), 403

    data = request.get_json()
    action = data["action"]
    with Session(engine) as database_session:
        if action == "add_trek":
            trek = Trek(
                trek_name=data["trek_name"],
                location=data["location"],
                difficulty=data["difficulty"],
                duration_days=int(data["duration_days"]),
                available_slots=int(data["available_slots"]),
                start_date=date.fromisoformat(data["start_date"]),
                end_date=date.fromisoformat(data["end_date"]),
            )
            database_session.add(trek)
            database_session.commit()
            return jsonify({"message": "Trek added."})

        if action == "update_trek":
            trek = database_session.get(Trek, int(data["trek_id"]))
            trek.trek_name = data["trek_name"]
            trek.location = data["location"]
            trek.difficulty = data["difficulty"]
            trek.duration_days = int(data["duration_days"])
            trek.available_slots = int(data["available_slots"])
            trek.status = data["status"]
            trek.start_date = date.fromisoformat(data["start_date"])
            trek.end_date = date.fromisoformat(data["end_date"])
            database_session.commit()
            return jsonify({"message": "Trek updated."})

        if action == "delete_trek":
            trek = database_session.get(Trek, int(data["trek_id"]))
            if trek and not trek.bookings:
                database_session.delete(trek)
                database_session.commit()
                return jsonify({"message": "Trek removed."})
            return jsonify({"message": "A trek with bookings cannot be removed."}), 400

        if action == "add_staff":
            email = data["email"].strip().lower()
            existing_user = database_session.query(User).filter_by(email=email).first()
            if existing_user:
                return jsonify({"message": "An account with this email already exists."}), 400
            staff_user = User(
                name=data["name"],
                email=email,
                password_hash=generate_password_hash(data["password"]),
                role="Trek Staff",
            )
            database_session.add(staff_user)
            database_session.flush()
            staff_profile = StaffProfile(
                user_id=staff_user.user_id,
                contact_details=data["contact_details"],
            )
            database_session.add(staff_profile)
            database_session.commit()
            return jsonify({"message": "Staff member added."})

        if action == "assign_staff":
            trek = database_session.get(Trek, int(data["trek_id"]))
            trek.assigned_staff_id = int(data["staff_id"]) if data["staff_id"] else None
            database_session.commit()
            return jsonify({"message": "Staff assignment updated."})

        if action == "change_status":
            user = database_session.get(User, int(data["user_id"]))
            user.status = data["status"]
            if user.staff_profile:
                user.staff_profile.status = data["status"]
            database_session.commit()
            return jsonify({"message": "Account status updated."})

    return jsonify({"message": "Action not found."}), 404


@main.route("/staff")
def staff_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") != "Trek Staff":
        return "Unauthorized", 403
    return render_template("staff_dashboard.html")


@main.route("/api/staff/treks")
def staff_treks():
    if not session.get("user_id"):
        return jsonify({"message": "Please log in."}), 401
    if session.get("role") != "Trek Staff":
        return jsonify({"message": "Unauthorized."}), 403

    with Session(engine) as database_session:
        staff = database_session.query(StaffProfile).filter_by(user_id=session["user_id"]).first()
        if staff is None:
            return jsonify({"message": "Staff profile not found."}), 404

        treks = database_session.query(Trek).filter_by(assigned_staff_id=staff.staff_id).order_by(Trek.trek_id).all()
        trek_list = []
        for trek in treks:
            bookings = database_session.query(Booking).options(
                joinedload(Booking.user)
            ).filter_by(trek_id=trek.trek_id).all()
            participants = [{
                "name": booking.user.name,
                "email": booking.user.email,
                "status": booking.status,
            } for booking in bookings if booking.status == "Booked"]
            trek_list.append({
                "trek_id": trek.trek_id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "difficulty": trek.difficulty,
                "duration_days": trek.duration_days,
                "available_slots": trek.available_slots,
                "status": trek.status,
                "start_date": trek.start_date.isoformat() if trek.start_date else "",
                "end_date": trek.end_date.isoformat() if trek.end_date else "",
                "registered_count": len(participants),
                "participants": participants,
            })
        return jsonify({"treks": trek_list})


@main.route("/api/staff/treks/<int:trek_id>", methods=["POST"])
def update_staff_trek(trek_id):
    if not session.get("user_id"):
        return jsonify({"message": "Please log in."}), 401
    if session.get("role") != "Trek Staff":
        return jsonify({"message": "Unauthorized."}), 403

    data = request.get_json()
    available_slots = int(data["available_slots"])
    if available_slots < 0:
        return jsonify({"message": "Available slots cannot be negative."}), 400
    if data["status"] not in ["Open", "Closed", "Started", "Ongoing", "Completed"]:
        return jsonify({"message": "Invalid trek status."}), 400

    with Session(engine) as database_session:
        staff = database_session.query(StaffProfile).filter_by(user_id=session["user_id"]).first()
        trek = database_session.get(Trek, trek_id)
        if staff is None or trek is None or trek.assigned_staff_id != staff.staff_id:
            return jsonify({"message": "This trek is not assigned to you."}), 403

        trek.available_slots = available_slots
        trek.status = data["status"]
        database_session.commit()
        return jsonify({"message": "Trek updated."})


@main.route("/trekker", defaults={"page": "dashboard"})
@main.route("/trekker/<page>")
def trekker_dashboard(page):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") != "Trekker":
        return "Unauthorized", 403

    page_templates = {
        "dashboard": "trekker_dashboard.html",
        "profile": "trekker_profile.html",
        "treks": "trekker_treks.html",
        "bookings": "trekker_bookings.html",
    }
    return render_template(page_templates.get(page, "trekker_dashboard.html"))


@main.route("/api/trekker/dashboard")
def trekker_dashboard_data():
    if not session.get("user_id") or session.get("role") != "Trekker":
        return jsonify({"message": "Unauthorized."}), 403

    with Session(engine) as database_session:
        user = database_session.get(User, session["user_id"])
        bookings = database_session.query(Booking).options(
            joinedload(Booking.trek)
        ).filter_by(user_id=user.user_id).order_by(Booking.booking_date.desc()).all()
        return jsonify({
            "name": user.name,
            "available_treks": database_session.query(Trek).filter(
                Trek.status == "Open", Trek.available_slots > 0
            ).count(),
            "bookings": [{
                "booking_id": booking.booking_id,
                "trek_name": booking.trek.trek_name,
                "booking_status": booking.status,
                "trek_status": booking.trek.status,
            } for booking in bookings],
        })


@main.route("/api/trekker/profile", methods=["GET", "POST"])
def trekker_profile():
    if not session.get("user_id") or session.get("role") != "Trekker":
        return jsonify({"message": "Unauthorized."}), 403

    with Session(engine) as database_session:
        user = database_session.get(User, session["user_id"])
        if request.method == "GET":
            return jsonify({"name": user.name, "email": user.email})

        data = request.get_json()
        email = data["email"].strip().lower()
        existing_user = database_session.query(User).filter(
            User.email == email, User.user_id != user.user_id
        ).first()
        if existing_user:
            return jsonify({"message": "An account with this email already exists."}), 400

        user.name = data["name"].strip()
        user.email = email
        database_session.commit()
        session["user_name"] = user.name
        return jsonify({"message": "Profile updated."})


@main.route("/api/trekker/treks")
def trekker_treks():
    if not session.get("user_id") or session.get("role") != "Trekker":
        return jsonify({"message": "Unauthorized."}), 403

    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    location = request.args.get("location", "").strip()
    duration = request.args.get("duration", "").strip()

    with Session(engine) as database_session:
        treks_query = database_session.query(Trek).filter_by(status="Open")
        if search:
            treks_query = treks_query.filter(Trek.trek_name.ilike(f"%{search}%"))
        if difficulty:
            treks_query = treks_query.filter_by(difficulty=difficulty)
        if location:
            treks_query = treks_query.filter(Trek.location.ilike(f"%{location}%"))
        if duration.isdigit():
            treks_query = treks_query.filter_by(duration_days=int(duration))

        treks = treks_query.order_by(Trek.trek_id).all()
        return jsonify({"treks": [{
            "trek_id": trek.trek_id,
            "trek_name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration_days": trek.duration_days,
            "available_slots": trek.available_slots,
            "status": trek.status,
            "start_date": trek.start_date.isoformat() if trek.start_date else "",
            "end_date": trek.end_date.isoformat() if trek.end_date else "",
        } for trek in treks]})


@main.route("/api/trekker/bookings")
def trekker_bookings():
    if not session.get("user_id") or session.get("role") != "Trekker":
        return jsonify({"message": "Unauthorized."}), 403

    with Session(engine) as database_session:
        bookings = database_session.query(Booking).options(
            joinedload(Booking.trek)
        ).filter_by(user_id=session["user_id"]).order_by(Booking.booking_date.desc()).all()
        return jsonify({"bookings": [{
            "booking_id": booking.booking_id,
            "trek_name": booking.trek.trek_name,
            "location": booking.trek.location,
            "start_date": booking.trek.start_date.isoformat() if booking.trek.start_date else "",
            "end_date": booking.trek.end_date.isoformat() if booking.trek.end_date else "",
            "booking_status": booking.status,
            "trek_status": booking.trek.status,
            "booking_date": booking.booking_date.isoformat(),
        } for booking in bookings]})


@main.route("/api/trekker/bookings", methods=["POST"])
def create_trekker_booking():
    if not session.get("user_id") or session.get("role") != "Trekker":
        return jsonify({"message": "Unauthorized."}), 403

    data = request.get_json()
    with Session(engine) as database_session:
        trek = database_session.get(Trek, int(data["trek_id"]))
        if trek is None or trek.status != "Open":
            return jsonify({"message": "This trek is closed or unavailable."}), 400

        existing_booking = database_session.query(Booking).filter_by(
            user_id=session["user_id"], trek_id=trek.trek_id
        ).first()
        if existing_booking:
            return jsonify({"message": "You have already booked this trek."}), 400

        if trek.available_slots <= 0:
            return jsonify({"message": "No slots are available for this trek."}), 400

        booking = Booking(user_id=session["user_id"], trek_id=trek.trek_id)
        trek.available_slots -= 1
        database_session.add(booking)
        database_session.commit()
        return jsonify({"message": "Trek booked successfully."})
