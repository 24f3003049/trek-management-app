import os
from datetime import date
from flask import Flask, render_template
from config import Config, db, login_manager


#model ki tables import 
from models.user import User
from models.trek import Trek
from models.booking import Booking
from models.profile import Profile


def create_app():
    # Flask app initialize 
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database aur login manager setup 
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Setup directories
    os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)

    # User loader 
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.admin_controller import admin_bp
    from controllers.staff_controller import staff_bp
    from controllers.user_controller import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)

    # Database initialization and seeding
    with app.app_context():
        db.create_all()
        #  default admin accounts exist with known credentials 
        # preexisting adminn
        default_admins = [
            {
                "name": "Administrator",
                "email": "admin@gmail.com",
                "password": "admin123",
                "contact": "9999999999",
            },
            {
                "name": "pawnie",
                "email": "pawnie@gmail.com",
                "password": "madebyme",
                "contact": "9999999999",
            },
        ]

        for admin_data in default_admins:
            admin_user = User.query.filter_by(email=admin_data["email"]).first()
            if not admin_user:
                admin_user = User(
                    name=admin_data["name"],
                    email=admin_data["email"],
                    password=admin_data["password"],
                    role="admin",
                    status="approved",
                    is_blacklisted=False,
                    contact=admin_data["contact"],
                )
                db.session.add(admin_user)
                db.session.commit()
                profile = Profile(user_id=admin_user.id)
                db.session.add(profile)
                db.session.commit()
            else:
                admin_user.password = admin_data["password"]
                admin_user.role = "admin"
                admin_user.status = "approved"
                admin_user.is_blacklisted = False
                if not admin_user.profile:
                    db.session.add(Profile(user_id=admin_user.id))
                db.session.commit()

        # Sample treks add kar rahe hain - practice k liye
        bookable_count = Trek.query.filter(Trek.status.in_(["Open", "Approved"])).count()
        if bookable_count == 0:
            sample_treks = [
                Trek(
                    name="Valley of Flowers",
                    location="Uttarakhand",
                    difficulty="Moderate",
                    duration=6,
                    available_slots=15,
                    description="A UNESCO World Heritage site with stunning alpine meadows.",
                    start_date=date(2026, 7, 15),
                    end_date=date(2026, 7, 20),
                    status="Open",
                ),
                Trek(
                    name="Kedarkantha",
                    location="Uttarakhand",
                    difficulty="Easy",
                    duration=5,
                    available_slots=20,
                    description="A popular winter trek with panoramic Himalayan views.",
                    start_date=date(2026, 12, 10),
                    end_date=date(2026, 12, 14),
                    status="Open",
                ),
                Trek(
                    name="Hampta Pass",
                    location="Himachal Pradesh",
                    difficulty="Moderate",
                    duration=5,
                    available_slots=12,
                    description="Cross from lush Kullu valley to the barren Lahaul region.",
                    start_date=date(2026, 6, 20),
                    end_date=date(2026, 6, 24),
                    status="Open",
                ),
            ]
            db.session.add_all(sample_treks)
            db.session.commit()

    # Home page route - landing page
    @app.route("/")
    def index():
        # Open treks which  book 
        open_treks = Trek.query.filter(Trek.status.in_(["Open", "Approved"])).all()
        return render_template("index.html", treks=open_treks)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)