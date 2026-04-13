import uuid
from datetime import datetime
from app import db


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id            = db.Column(db.Integer,    primary_key=True)
    # UUID ensures every ticket has a globally unique, non-guessable code
    ticket_code   = db.Column(db.String(36), unique=True, nullable=False,
                              default=lambda: str(uuid.uuid4()))
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)
    event_id      = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    qr_code_path  = db.Column(db.String(255), default='')   # filename of generated QR image
    status        = db.Column(db.String(20),  default='active')  # active | cancelled
    registered_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def get_qr_url(self):
        if self.qr_code_path:
            return f'/static/images/uploads/{self.qr_code_path}'
        return None

    def __repr__(self):
        return f'<Ticket {self.ticket_code}>'
