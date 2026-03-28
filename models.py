from datetime import datetime
from extensions import db
from sqlalchemy import UniqueConstraint

class User(db.Model):
    """Core User model representing an application user."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: One user can have many social connections.
    # Edge Case: If a user is deleted, all their social connections are removed (cascade).
    social_connections = db.relationship('SocialConnection', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

class SocialConnection(db.Model):
    """Model to store OAuth connections to platforms like Twitter or LinkedIn."""
    __tablename__ = 'social_connections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # e.g., 'twitter', 'linkedin'
    platform_user_id = db.Column(db.String(255), nullable=False)  # ID from the external platform
    scopes = db.Column(db.Text, nullable=True)  # Store granted scopes
    
    # OAuth tokens (Strictly managed via environment variables for security in production)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Edge Case: A user cannot connect the same platform twice.
    __table_args__ = (UniqueConstraint('user_id', 'platform', name='_user_platform_uc'),)

    def __repr__(self):
        return f'<SocialConnection {self.platform} for User {self.user_id}>'
