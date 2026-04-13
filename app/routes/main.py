from flask import Blueprint, render_template, request
from flask_login import current_user
from datetime import datetime
from app.models.event import Event, CATEGORIES
from app.models.user import User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    now = datetime.utcnow()

    # 6 next upcoming events for the featured section
    featured = (Event.query
                .filter(Event.date > now, Event.is_published == True)
                .order_by(Event.date.asc())
                .limit(6).all())

    # Personalised recommendations (only when logged in)
    recommended = []
    if current_user.is_authenticated and current_user.get_interests_list():
        from app.utils.recommender import get_recommended_events
        recommended = get_recommended_events(current_user, limit=3)

    total_events = Event.query.filter(Event.is_published == True).count()
    total_users  = User.query.count()

    return render_template('main/home.html',
                           featured=featured,
                           recommended=recommended,
                           categories=CATEGORIES,
                           total_events=total_events,
                           total_users=total_users,
                           now=now)


@main_bp.route('/search')
def search():
    q         = request.args.get('q', '').strip()
    category  = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to   = request.args.get('date_to', '')
    price_max = request.args.get('price_max', '')
    location  = request.args.get('location', '')

    query = Event.query.filter(Event.is_published == True)

    if q:
        like = f'%{q}%'
        query = query.filter(
            Event.title.ilike(like) |
            Event.description.ilike(like) |
            Event.location.ilike(like)
        )
    if category:
        query = query.filter(Event.category == category)
    if date_from:
        try:
            query = query.filter(Event.date >= datetime.strptime(date_from, '%Y-%m-%d'))
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Event.date <= datetime.strptime(date_to, '%Y-%m-%d'))
        except ValueError:
            pass
    if price_max:
        try:
            query = query.filter(Event.price <= float(price_max))
        except ValueError:
            pass
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))

    events = query.order_by(Event.date.asc()).all()

    return render_template('main/search.html',
                           events=events,
                           q=q,
                           category=category,
                           categories=CATEGORIES,
                           total=len(events))
