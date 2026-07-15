from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from config import db
from models.trek import Trek
from models.booking import Booking

user_bp = Blueprint("user", __name__, url_prefix="/user")


def user_required():
    if not current_user.is_authenticated or current_user.role != "user":
        abort(403)


@user_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    user_required()

    # Filter  - difficulty location 
    difficulty = request.args.get("difficulty", "All").strip()
    location = request.args.get("location", "").strip()

 
    trek_query = Trek.query.filter(Trek.status.in_(["Open", "Approved"]))

    if difficulty and difficulty != "All":
        trek_query = trek_query.filter_by(difficulty=difficulty)
    if location:
        trek_query = trek_query.filter(Trek.location.ilike(f"%{location}%"))

    available_treks = trek_query.all()

   
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()

    #  dashboard numbers
    total_available_treks = Trek.query.filter(Trek.status.in_(["Open", "Approved"])).count()
    my_bookings_count = Booking.query.filter_by(user_id=current_user.id, status="Booked").count()
    completed_bookings_count = Booking.query.filter_by(user_id=current_user.id, status="Completed").count()

    return render_template(
        "userdashboard.html",
        treks=available_treks,
        bookings=bookings,
        total_available=total_available_treks,
        my_bookings_count=my_bookings_count,
        completed_bookings_count=completed_bookings_count,
        difficulty_filter=difficulty,
        location_filter=location
    )


@user_bp.route("/bookings", methods=["GET"])
@login_required
def bookings():
    user_required()

    user_bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return render_template("bookinguser.html", bookings=user_bookings)


@user_bp.route("/book/<int:trek_id>", methods=["POST"])
@login_required
def book_trek(trek_id):
    user_required()

    trek = Trek.query.get_or_404(trek_id)

   
    if trek.status not in ["Open", "Approved"]:
        flash("This trek is currently not open for booking.", "danger")
        return redirect(url_for("user.dashboard"))

    
    if trek.available_slots <= 0:
        flash("Sorry, no slots available for this trek.", "danger")
        return redirect(url_for("user.dashboard"))

    
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id, status="Booked").first()
    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.dashboard"))

    try:
       
        booking = Booking(
            user_id=current_user.id,
            trek_id=trek.id,
            status="Booked",
            participants=1
        )
        trek.available_slots -= 1

        db.session.add(booking)
        db.session.commit()
        flash(f"Successfully booked trek '{trek.name}'!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error booking trek: {str(e)}", "danger")

    return redirect(url_for("user.dashboard"))


    



@user_bp.route("/booking/cancel/<int:booking_id>", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    user_required()

    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()

    if booking.status != "Booked":
        flash("Only active bookings can be cancelled.", "warning")
        return redirect(url_for("user.dashboard"))

    try:
        booking.status = "Cancelled"
        
      
        trek = Trek.query.get(booking.trek_id)
        if trek:
            trek.available_slots += 1

        db.session.commit()
        flash("Booking cancelled successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error cancelling booking: {str(e)}", "danger")

    return redirect(url_for("user.dashboard"))
