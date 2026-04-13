from datetime import datetime
from app import db

# All possible event categories
CATEGORIES = [
    'Music', 'Technology', 'Sports', 'Arts', 'Food & Drink',
    'Business', 'Education', 'Health', 'Travel', 'Gaming', 'Other'
]

# Icon mapping for each category (Bootstrap Icons)
CATEGORY_ICONS = {
    'Music':       'music-note-beamed',
    'Technology':  'cpu',
    'Sports':      'trophy',
    'Arts':        'palette',
    'Food & Drink':'cup-hot',
    'Business':    'briefcase',
    'Education':   'mortarboard',
    'Health':      'heart-pulse',
    'Travel':      'airplane',
    'Gaming':      'controller',
    'Other':       'calendar-event',
}

# Placeholder images per category (Unsplash)
CATEGORY_IMAGES = {
    'Music':       'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80',
    'Technology':  'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80',
    'Sports':      'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',
    'Arts':        'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800&q=80',
    'Food & Drink':'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80',
    'Business':    'https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=800&q=80',
    'Education':   'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800&q=80',
    'Health':      'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80',
    'Travel':      'https://images.unsplash.com/photo-1488085061387-422e29b40080?w=800&q=80',
    'Gaming':      'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&q=80',
    'Other':       'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80',
}


class Event(db.Model):
    __tablename__ = 'events'

    id           = db.Column(db.Integer,     primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text,        nullable=False)
    category     = db.Column(db.String(50),  nullable=False, index=True)
    location     = db.Column(db.String(200), nullable=False)
    latitude     = db.Column(db.Float,       nullable=True)   # for map pin
    longitude    = db.Column(db.Float,       nullable=True)
    date         = db.Column(db.DateTime,    nullable=False, index=True)
    end_date     = db.Column(db.DateTime,    nullable=True)
    image        = db.Column(db.String(255), default='')      # uploaded filename
    capacity     = db.Column(db.Integer,     default=100)
    price        = db.Column(db.Float,       default=0.0)
    is_virtual   = db.Column(db.Boolean,     default=False)
    meet_link    = db.Column(db.String(255), default='')
    is_published = db.Column(db.Boolean,     default=True)
    organizer_id = db.Column(db.Integer,     db.ForeignKey('users.id'), nullable=False)
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)

    # Relationships (cascade delete removes tickets/comments when event is deleted)
    tickets  = db.relationship('Ticket',  backref='event', lazy='dynamic',
                               cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='event', lazy='dynamic',
                               cascade='all, delete-orphan')

    # ── Computed properties ───────────────────────────────────
    @property
    def tickets_sold(self):
        return self.tickets.filter_by(status='active').count()

    @property
    def spots_left(self):
        return max(0, self.capacity - self.tickets_sold)

    @property
    def is_full(self):
        return self.spots_left == 0

    @property
    def is_upcoming(self):
        return self.date > datetime.utcnow()

    @property
    def is_past(self):
        return self.date < datetime.utcnow()

    @property
    def fill_percentage(self):
        """Percentage of seats filled — used by capacity progress bar."""
        if self.capacity == 0:
            return 100
        return min(100, int((self.tickets_sold / self.capacity) * 100))

    @property
    def price_display(self):
        return 'Free' if self.price == 0 else f'${self.price:.2f}'

    def get_image_url(self):
        """Return uploaded image or category-based placeholder."""
        if self.image:
            return f'/static/images/uploads/{self.image}'
        return CATEGORY_IMAGES.get(self.category, CATEGORY_IMAGES['Other'])

    def get_icon(self):
        return CATEGORY_ICONS.get(self.category, 'calendar-event')

    def __repr__(self):
        return f'<Event {self.title}>'
