from extensions import db
from datetime import date


class Trek(db.Model):

    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    location = db.Column(db.String(150), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration = db.Column(db.Integer, nullable=False)

    available_slots = db.Column(db.Integer, nullable=False)

    description = db.Column(db.Text)

    start_date = db.Column(db.Date, nullable=False)

    end_date = db.Column(db.Date, nullable=False)

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    image = db.Column(
        db.String(255)
    )

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Trek {self.name}>"