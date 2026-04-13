from datetime import datetime
from app.models.event import Event


def get_recommended_events(user, limit=6):
    """
    Content-based recommendation engine.

    Scoring rules:
      +3  event category matches one of the user's listed interests
      +2  event is within the next 14 days (happening soon)
      +1  event is within the next 30 days
      +1  per 10 tickets already sold (social proof / popularity)
      (already-registered events are excluded entirely)

    Returns a list of Event objects sorted by descending score.
    """
    now = datetime.utcnow()

    # IDs of events the user already has an active ticket for
    registered_ids = {
        t.event_id
        for t in user.tickets.filter_by(status='active').all()
    }

    interests = set(user.get_interests_list())

    # All upcoming published events the user hasn't registered for
    candidates = Event.query.filter(
        Event.date > now,
        Event.is_published == True
    ).all()

    scored = []
    for event in candidates:
        if event.id in registered_ids:
            continue

        score = 0

        # Interest match
        if event.category in interests:
            score += 3

        # Recency bonus
        days_until = (event.date - now).days
        if days_until <= 14:
            score += 2
        elif days_until <= 30:
            score += 1

        # Popularity bonus (capped at +2)
        score += min(2, event.tickets_sold // 10)

        scored.append((score, event.date, event))

    # Sort: highest score first, then earliest date
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [e for _, _, e in scored[:limit]]
