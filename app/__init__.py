import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from .models import db
from .utils.logging import configure_logging
from .routes.integration import integration_bp
from .routes.auth import auth_bp
from .middleware.logging import LoggingMiddleware


def create_app(config_class=None):
    # Create and configure the Flask application
    app = Flask(__name__)

    # Initialize Swagger
    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Hubspot CRM API",
            'swagger_ui': True,
        }
    )

    # Load configuration
    if config_class is None:
        env = os.environ.get("FLASK_ENV", "default")
        from .config import config

        app.config.from_object(config[env])
    else:
        app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Configure logging
    configure_logging(app)

    # Register middleware
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(integration_bp, url_prefix='/api')
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}, 200

    return app
