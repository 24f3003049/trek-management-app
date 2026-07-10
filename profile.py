from extensions import db


class Profile(db.Model):

    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    age = db.Column(db.Integer)

    gender = db.Column(db.String(20))

    address = db.Column(db.Text)

    emergency_contact = db.Column(db.String(15))

    blood_group = db.Column(db.String(10))

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True
    )

    def __repr__(self):
        return f"<Profile {self.id}>"