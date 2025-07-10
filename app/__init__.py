from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import and register blueprints here if you expand the app
    # For now, we'll import routes directly
    with app.app_context():
        from . import routes

    return app