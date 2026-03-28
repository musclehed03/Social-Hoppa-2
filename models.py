from datetime import datetime
from extensions import db

class User(db.Model):
    """User model for authentication and social connections."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Relationship: A user can have multiple social connections.
    social_connections = db.relationship('SocialConnection', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.email}>'

class SocialConnection(db.Model):
    """Model to store social platform connections for a user."""
    __tablename__ = 'social_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform_name = db.Column(db.String(50), nullable=False)
    platform_user_id = db.Column(db.String(255), nullable=True)  # ID from the external platform
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    scopes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<SocialConnection {self.platform_name} for User {self.user_id}>'
