import bcrypt
from datetime import datetime
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False, index=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20),  default='user')   # 'user' | 'admin'
    avatar        = db.Column(db.String(255), default='')
    bio           = db.Column(db.Text,        default='')
    interests     = db.Column(db.String(500), default='')       # comma-separated categories
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    # Relationships
    organized_events = db.relationship('Event', backref='organizer', lazy='dynamic',
                                       foreign_keys='Event.organizer_id')
    tickets          = db.relationship('Ticket',       backref='user',   lazy='dynamic')
    comments         = db.relationship('Comment',      backref='author', lazy='dynamic')
    notifications    = db.relationship('Notification', backref='user',   lazy='dynamic')

    # ── Password helpers ──────────────────────────────────────
    def set_password(self, password):
        """Hash and store password securely with bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), salt
        ).decode('utf-8')

    def check_password(self, password):
        """Return True if the plain password matches the stored hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    # ── Interest helpers ──────────────────────────────────────
    def get_interests_list(self):
        """Return interests as a Python list."""
        if self.interests:
            return [i.strip() for i in self.interests.split(',') if i.strip()]
        return []

    def set_interests_list(self, items):
        """Store a Python list as a comma-separated string."""
        self.interests = ', '.join(items)

    # ── Properties ───────────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_unread_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def get_avatar_url(self):
        """Return uploaded avatar URL, or auto-generated placeholder."""
        if self.avatar:
            return f'/static/images/uploads/{self.avatar}'
        return (f'https://ui-avatars.com/api/?name={self.username}'
                f'&background=6C63FF&color=fff&size=128&bold=true')

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
