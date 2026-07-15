from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from config import db
from models.user import User
from models.trek import Trek
from models.booking import Booking

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


def staff_required():
    if not current_user.is_authenticated or current_user.role != "staff":
        abort(403)


@staff_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    staff_required()

    # Check if staff is approved by admin
    if current_user.status != "approved":
        return render_template("staff_pending.html")

  
    assigned_treks = Trek.query.filter_by(staff_id=current_user.id).all()


    trek_ids = [t.id for t in assigned_treks]
    bookings = []
    if trek_ids:
        bookings = Booking.query.filter(Booking.trek_id.in_(trek_ids)).all()

    return render_template(
        "staffdashboard.html",
        treks=assigned_treks,
        bookings=bookings
    )


@staff_bp.route("/trek/update/<int:trek_id>", methods=["POST"])
@login_required
def update_trek(trek_id):
    staff_required()

    if current_user.status != "approved":
        abort(403)

    trek = Trek.query.filter_by(id=trek_id, staff_id=current_user.id).first_or_404()

    try:
        available_slots = int(request.form.get("available_slots"))
        status = request.form.get("status")

        if available_slots < 0:
            flash("Available slots cannot be negative.", "danger")
            return redirect(url_for("staff.dashboard"))

        if status not in ["Open", "Closed", "Completed", "Pending", "Approved"]:
            flash("Invalid trek status.", "danger")
            return redirect(url_for("staff.dashboard"))

        trek.available_slots = available_slots
        trek.status = status
        db.session.commit()
        flash(f"Trek '{trek.name}' updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating trek: {str(e)}", "danger")

    return redirect(url_for("staff.dashboard"))
