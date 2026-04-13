# Import all models so SQLAlchemy can discover and create their tables
from app.models.user         import User
from app.models.event        import Event
from app.models.ticket       import Ticket
from app.models.comment      import Comment
from app.models.notification import Notification
