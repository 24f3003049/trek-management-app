from config import db
from datetime import datetime


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column( db.DateTime,default=datetime.utcnow )
    status = db.Column(db.String(20),default="Booked")
    participants = db.Column(
        db.Integer,
  default=1)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Booking {self.id}>"
