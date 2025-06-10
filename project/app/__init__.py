from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)

    from .routes.auth_routes import auth_bp
    from .routes.customer_routes import customer_bp
    from .routes.owner_routes import owner_bp
    from .routes.rider_routes import rider_bp
    from .routes.api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(owner_bp, url_prefix='/owner')
    app.register_blueprint(rider_bp, url_prefix='/rider')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    with app.app_context():
        from . import models

    return app