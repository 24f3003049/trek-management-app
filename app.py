import os
from flask import Flask, render_template, redirect, url_for
from config import Config
from extensions import db, login_manager, migrate
from werkzeug.security import generate_password_hash

# Import models to ensure they are registered with SQLAlchemy
from models.user import User
from models.trek import Trek
from models.booking import Booking
from models.profile import Profile


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Setup directories
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.admin_controller import admin_bp
    from controllers.staff_controller import staff_bp
    from controllers.user_controller import user_bp
    from controllers.booking_controller import booking_bp
    from controllers.search_controller import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(search_bp)

    # Database initialization and seeding
    with app.app_context():
        db.create_all()

        # Seed default admin user if not present
        admin_user = User.query.filter_by(email="admin@gmail.com").first()
        if not admin_user:
            admin = User(
                name="Administrator",
                email="admin@gmail.com",
                password=generate_password_hash("admin123"),
                role="admin",
                status="approved",
                is_blacklisted=False,
                contact="9999999999"
            )
            db.session.add(admin)
            db.session.commit()
            
            # Create profile for admin
            profile = Profile(user_id=admin.id)
            db.session.add(profile)
            db.session.commit()

        # Seed pawnie admin user if not present
        pawnie_user = User.query.filter_by(email="pawnie@gmail.com").first()
        if not pawnie_user:
            pawnie = User(
                name="pawnie",
                email="pawnie@gmail.com",
                password=generate_password_hash("madebyme"),
                role="admin",
                status="approved",
                is_blacklisted=False,
                contact="9999999999"
            )
            db.session.add(pawnie)
            db.session.commit()
            
            profile = Profile(user_id=pawnie.id)
            db.session.add(profile)
            db.session.commit()

    @app.route("/")
    def index():
        # Fetch open treks for the landing page
        open_treks = Trek.query.filter(Trek.status.in_(["Open", "Approved"])).all()
        return render_template("index.html", treks=open_treks)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
