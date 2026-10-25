from flask import Blueprint, redirect, render_template, session, url_for


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


@main.route("/admin")
def admin_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") != "Admin":
        return "Unauthorized", 403
    return render_template("admin_dashboard.html", user_name=session.get("user_name"))


@main.route("/staff")
def staff_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") != "Trek Staff":
        return "Unauthorized", 403
    return render_template("staff_dashboard.html", user_name=session.get("user_name"))


@main.route("/trekker")
def trekker_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    if session.get("role") != "Trekker":
        return "Unauthorized", 403
    return render_template("trekker_dashboard.html", user_name=session.get("user_name"))
