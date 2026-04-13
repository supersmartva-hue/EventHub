from datetime import datetime
from app import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id         = db.Column(db.Integer,    primary_key=True)
    user_id    = db.Column(db.Integer,    db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    link       = db.Column(db.String(255), default='')   # URL to navigate to on click
    is_read    = db.Column(db.Boolean,     default=False)
    created_at = db.Column(db.DateTime,   default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id} → User {self.user_id}>'
