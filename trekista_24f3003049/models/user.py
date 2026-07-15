from config import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(15))
    # Role  admin, staff, ya user
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20),default="pending")
    
    # Blacklist flag - 
    is_blacklisted = db.Column( db.Boolean, default=False)
    created_at = db.Column( db.DateTime, default=datetime.utcnow )
# relations w ohter table
    assigned_treks = db.relationship(
        "Trek",
        backref="assigned_staff",
        lazy=True
    )

    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    profile = db.relationship(
        "Profile",
        backref="user",
        uselist=False,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.name}>"
    