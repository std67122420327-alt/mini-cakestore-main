import os
from flask import Flask
from cakestore.extensions import db, login_manager, bcrypt
from cakestore.models import User, Category, Cake
from cakestore.cake_categories import CAKE_NAMES
from cakestore.core.routes import core_bp
from cakestore.users.routes import user_bp
from cakestore.cakes.routes import cake_bp

# Load environment variables from .env file (for local development only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, using system environment variables (production)

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'warning'
    login_manager.login_message = 'Please log in to access this page.'
    bcrypt.init_app(app)

    app.register_blueprint(core_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(cake_bp, url_prefix='/cake')

    with app.app_context():
        # Ensure tables and category master data exist for a new database.
        db.create_all()
        existing_names = set(db.session.scalars(db.select(Category.name)).all())
        missing_names = [name for name in CAKE_NAMES if name not in existing_names]
        if missing_names:
            db.session.add_all([Category(name=name) for name in missing_names])
            db.session.commit()

    return app
