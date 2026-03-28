import os
from flask import Flask
from extensions import db
from models import User

def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__)

    # Configuration using environment variables (Strict Constraint)
    # Defaulting to SQLite for local dev, but expecting PostgreSQL in prod
    database_uri = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    
    # Handle Heroku-style 'postgres://' vs SQLAlchemy-required 'postgresql://'
    if database_uri.startswith("postgres://"):
        database_uri = database_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Securely retrieve Flask Secret Key for session management (Strict Constraint)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-only-not-for-prod')

    # Initialize extensions with the app context
    db.init_app(app)

    # Register Blueprints
    from twitter_routes import twitter_bp
    app.register_blueprint(twitter_bp)

    # Create tables if they don't exist (useful for simple scaffolding)
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    # Bind to 0.0.0.0 and use PORT env var for Cloud Run compatibility
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
