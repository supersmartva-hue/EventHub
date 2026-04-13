import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

from config import config

# ─── Initialize extensions (not yet attached to any app) ──────
# We create them here so they can be imported anywhere in the app
db       = SQLAlchemy()        # Database
login    = LoginManager()      # User sessions
mail     = Mail()              # Email sending
migrate  = Migrate()           # DB migrations
socketio = SocketIO()          # Real-time events
csrf     = CSRFProtect()       # Global CSRF protection


def create_app(config_name='default'):
    """
    App Factory Function.

    Instead of creating the Flask app globally, we use a factory.
    This makes testing easier and allows multiple configurations.

    Usage:
        app = create_app('development')
        app = create_app('production')
    """

    app = Flask(__name__)

    # ── Load configuration from config.py ─────────────────────
    app.config.from_object(config[config_name])

    # ── Create upload folder if it doesn't exist ──────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Attach extensions to this app instance ─────────────────
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    # ── Configure Flask-Login ──────────────────────────────────
    login.init_app(app)
    login.login_view     = 'auth.login'   # Redirect here if not logged in
    login.login_message  = 'Please log in to access this page.'
    login.login_message_category = 'warning'

    # ── Register Blueprints (route groups) ────────────────────
    # A Blueprint is a group of related routes.
    # We keep them in separate files to stay organized.

    from app.routes.main   import main_bp
    from app.routes.auth   import auth_bp
    from app.routes.events import events_bp
    from app.routes.tickets import tickets_bp
    from app.routes.admin  import admin_bp
    from app.routes.api    import api_bp

    app.register_blueprint(main_bp)                      # /
    app.register_blueprint(auth_bp,    url_prefix='/auth')    # /auth/...
    app.register_blueprint(events_bp,  url_prefix='/events')  # /events/...
    app.register_blueprint(tickets_bp, url_prefix='/tickets') # /tickets/...
    app.register_blueprint(admin_bp,   url_prefix='/admin')   # /admin/...
    app.register_blueprint(api_bp,     url_prefix='/api')     # /api/...

    # ── Register error handlers ────────────────────────────────
    from app.errors import register_errors
    register_errors(app)

    # ── Context processors ─────────────────────────────────────
    # Makes `now` available in every template automatically.
    from datetime import datetime as _dt
    @app.context_processor
    def inject_now():
        return {'now': _dt.utcnow()}

    # ── Create database tables (if they don't exist) ───────────
    # NOTE: we use 'from app import models' (not 'import app.models') so we
    # don't shadow the local variable 'app' (which holds the Flask instance).
    with app.app_context():
        from app import models as _models  # noqa: F401
        db.create_all()

    return app
