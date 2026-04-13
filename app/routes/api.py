from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.event        import Event
from app.models.notification import Notification

api_bp = Blueprint('api', __name__)

# ── Calendar endpoint ─────────────────────────────────────────
@api_bp.route('/events/calendar')
def events_calendar():
    """Return all published events in FullCalendar-compatible JSON."""
    events = Event.query.filter(Event.is_published == True).all()
    return jsonify([{
        'id':              e.id,
        'title':           e.title,
        'start':           e.date.isoformat(),
        'end':             e.end_date.isoformat() if e.end_date else None,
        'url':             f'/events/{e.id}',
        'backgroundColor': _cat_color(e.category),
        'borderColor':     _cat_color(e.category),
        'extendedProps': {
            'location': e.location,
            'category': e.category,
            'price':    e.price_display,
        }
    } for e in events])


# ── Search suggestions (autocomplete) ─────────────────────────
@api_bp.route('/search/suggestions')
def search_suggestions():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    events = (Event.query
              .filter(Event.title.ilike(f'%{q}%'), Event.is_published == True)
              .limit(6).all())
    return jsonify([{'id': e.id, 'title': e.title, 'category': e.category}
                    for e in events])


# ── Notifications ─────────────────────────────────────────────
@api_bp.route('/notifications')
@login_required
def get_notifications():
    notifs = (current_user.notifications
              .order_by(Notification.created_at.desc())
              .limit(10).all())
    return jsonify([{
        'id':      n.id,
        'message': n.message,
        'link':    n.link,
        'is_read': n.is_read,
        'time':    n.created_at.strftime('%b %d, %H:%M')
    } for n in notifs])


@api_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_read():
    (current_user.notifications
     .filter_by(is_read=False)
     .update({'is_read': True}))
    db.session.commit()
    return jsonify({'status': 'ok'})


# ── Unread count (for navbar badge) ──────────────────────────
@api_bp.route('/notifications/count')
@login_required
def notif_count():
    return jsonify({'count': current_user.get_unread_count()})


# ── Helpers ───────────────────────────────────────────────────
def _cat_color(category):
    return {
        'Music':       '#FF6584',
        'Technology':  '#6C63FF',
        'Sports':      '#43D9AD',
        'Arts':        '#FF9F43',
        'Food & Drink':'#FD7272',
        'Business':    '#4B7BEC',
        'Education':   '#A29BFE',
        'Health':      '#00CEC9',
        'Travel':      '#FDCB6E',
        'Gaming':      '#6C5CE7',
    }.get(category, '#6C63FF')
