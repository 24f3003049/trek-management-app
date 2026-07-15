from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from config import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register/user", methods=["GET", "POST"])
def register_user():
    # Agar pehle se logged in hai toh dashboard
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        contact = request.form.get("contact", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation checks
        if not all([name, email, contact, password, confirm]):
            flash("All fields are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            new_user = User(
                name=name,
                email=email,
                contact=contact,
                password=password,
                role="user",
                status="approved",
                is_blacklisted=False,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("User registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("userlogin.html", register=True, role="user")


@auth_bp.route("/register/staff", methods=["GET", "POST"])
def register_staff():
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        contact = request.form.get("contact", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Sab validation checks
        if not all([name, email, contact, password, confirm]):
            flash("All fields are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            new_staff = User(
                name=name,
                email=email,
                contact=contact,
                password=password,
                role="staff",
                status="pending",  # Admin approve
                is_blacklisted=False,
            )
            db.session.add(new_staff)
            db.session.commit()
            flash("Staff registration successful! Pending administrator approval.", "info")
            return redirect(url_for("auth.login"))

    return render_template("userlogin.html", register=True, role="staff")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        # User database query searching 
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            if user.is_blacklisted:
                flash("Your account has been blacklisted by the Administrator.", "danger")
            else:
                login_user(user)
                flash(f"Welcome back, {user.name}!", "success")
                return redirect_to_dashboard(user)
        else:
            # Wrong credentials
            flash("Invalid email or password.", "danger")

    return render_template("loginpage.html")

# Logout route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


def redirect_to_dashboard(user):
    # Admin ka dashboard
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    # Staff ka dashboard
    elif user.role == "staff":
        return redirect(url_for("staff.dashboard"))
    # Normal user ka dashboard
    return redirect(url_for("user.dashboard"))
