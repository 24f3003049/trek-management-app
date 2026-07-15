from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from config import db
from models.user import User
from models.trek import Trek
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Helper function - check  admin or not 
def admin_required():
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)


@admin_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    admin_required()

    # Search query
    query = request.args.get("q", "").strip()

    # Get search results if query exists, else get all records
    if query:
    
        if query.isdigit():
            treks = Trek.query.filter((Trek.id == int(query)) | (Trek.name.ilike(f"%{query}%"))).all()
            staff_members = User.query.filter(
                (User.role == "staff") & ((User.id == int(query)) | (User.name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%")))
            ).all()
            users = User.query.filter(
                (User.role == "user") & ((User.id == int(query)) | (User.name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%")))
            ).all()
        else:
            treks = Trek.query.filter(Trek.name.ilike(f"%{query}%") | Trek.location.ilike(f"%{query}%")).all()
            staff_members = User.query.filter(
                (User.role == "staff") & ((User.name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%")))
            ).all()
            users = User.query.filter(
                (User.role == "user") & ((User.name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%")))
            ).all()
    else:
        treks = Trek.query.all()
        staff_members = User.query.filter_by(role="staff").all()
        users = User.query.filter_by(role="user").all()

    # dashboard numbers
    total_treks = Trek.query.count()
    total_staff = User.query.filter_by(role="staff").count()
    total_users = User.query.filter_by(role="user", is_blacklisted=False ).count()
    pending_approvals = User.query.filter_by(role="staff", status="pending").count()

    # Get list of approved/active staff for assignment dropdown
    active_staff = User.query.filter_by(role="staff", status="approved", is_blacklisted=False).all()

    return render_template(
        "admindashboard.html",
        treks=treks,
        staff_members=staff_members,
        users=users,
        total_treks=total_treks,
        total_staff=total_staff,
        total_users=total_users,
        pending_approvals=pending_approvals,
        active_staff=active_staff,
        search_query=query
    )


@admin_bp.route("/trek/add", methods=["GET", "POST"])
@login_required
def add_trek():
    admin_required()

    if request.method == "POST":
        staff_id = request.form.get("staff_id")
        if staff_id == "":
            staff_id = None
        else:
            staff_id = int(staff_id)

        try:
        
            start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
            end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
            
            new_trek = Trek(
                name=request.form.get("name"),
                location=request.form.get("location"),
                difficulty=request.form.get("difficulty"),
                duration=int(request.form.get("duration")),
                available_slots=int(request.form.get("total_slots")),
                description=request.form.get("description"),
                start_date=start_date,
                end_date=end_date,
                status=request.form.get("status", "Pending"),
                staff_id=staff_id
            )
            db.session.add(new_trek)
            db.session.commit()
            flash("Trek created successfully!", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash(f"Error creating trek: {str(e)}", "danger")

    active_staff = User.query.filter_by(role="staff", status="approved", is_blacklisted=False).all()
    return render_template("trek_form.html", active_staff=active_staff, action="Add")


@admin_bp.route("/trek/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):
    admin_required()
    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":
        staff_id = request.form.get("staff_id")
        if staff_id == "" or staff_id is None:
            staff_id = None
        else:
            staff_id = int(staff_id)

        try:
            trek.name = request.form.get("name")
            trek.location = request.form.get("location")
            trek.difficulty = request.form.get("difficulty")
            trek.duration = int(request.form.get("duration"))
            trek.available_slots = int(request.form.get("total_slots"))
            trek.description = request.form.get("description")
            trek.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
            trek.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
            trek.status = request.form.get("status")
            trek.staff_id = staff_id

            db.session.commit()
            flash("Trek updated successfully!", "success")
            return redirect(url_for("admin.dashboard"))
        except Exception as e:
            flash(f"Error updating trek: {str(e)}", "danger")

    active_staff = User.query.filter_by(role="staff", status="approved", is_blacklisted=False).all()
    return render_template("trek_form.html", trek=trek, active_staff=active_staff, action="Edit")


@admin_bp.route("/trek/delete/<int:trek_id>", methods=["POST", "GET"])
@login_required
def delete_trek(trek_id):
    admin_required()
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted successfully!", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/staff/approve/<int:staff_id>", methods=["POST", "GET"])
@login_required
def approve_staff(staff_id):
    admin_required()
    staff = User.query.filter_by(id=staff_id, role="staff").first_or_404()
    staff.status = "approved"
    db.session.commit()
    flash(f"Staff '{staff.name}' approved successfully!", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/staff/blacklist/<int:staff_id>", methods=["POST", "GET"])
@login_required
def toggle_blacklist_staff(staff_id):
    admin_required()
    staff = User.query.filter_by(id=staff_id, role="staff").first_or_404()
    staff.is_blacklisted = not staff.is_blacklisted
    db.session.commit()
    status_str = "blacklisted" if staff.is_blacklisted else "removed from blacklist"
    flash(f"Staff '{staff.name}' {status_str} successfully!", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/blacklist/<int:user_id>", methods=["POST", "GET"])
@login_required
def toggle_blacklist_user(user_id):
    admin_required()
    user = User.query.filter_by(id=user_id, role="user").first_or_404()
    user.is_blacklisted = not user.is_blacklisted
    db.session.commit()
    status_str = "blacklisted" if user.is_blacklisted else "removed from blacklist"
    flash(f"User '{user.name}' {status_str} successfully!", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/trek/assign/<int:trek_id>", methods=["POST"])
@login_required
def assign_staff(trek_id):
    admin_required()
    trek = Trek.query.get_or_404(trek_id)
    staff_id = request.form.get("staff_id")
    if staff_id == "" or staff_id is None:
        trek.staff_id = None
        flash("Staff unassigned from trek.", "info")
    else:
        staff = User.query.filter_by(id=int(staff_id), role="staff", status="approved").first_or_404()
        trek.staff_id = staff.id
        flash(f"Staff '{staff.name}' successfully assigned to trek '{trek.name}'!", "success")
    db.session.commit()
    return redirect(url_for("admin.dashboard"))
