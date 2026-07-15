from config import db


class Profile(db.Model):

    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    address = db.Column(db.Text)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True
    )

    def __repr__(self):
        return f"<Profile {self.id}>"