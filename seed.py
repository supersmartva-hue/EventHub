"""
seed.py — Populate the database with sample data for testing.

Run once:  python seed.py
"""

from datetime import datetime, timedelta
import random
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user   import User
from app.models.event  import Event, CATEGORIES

flask_app = create_app()

SAMPLE_EVENTS = [
    ("TechConf 2026",          "Technology", "New York, NY",        40.7128, -74.0060, 200, 49.99),
    ("Rock Night Out",         "Music",      "Los Angeles, CA",     34.0522,-118.2437, 500, 25.00),
    ("Marathon City Run",      "Sports",     "Chicago, IL",         41.8781, -87.6298, 1000, 0.0),
    ("AI & Future Summit",     "Technology", "San Francisco, CA",   37.7749,-122.4194, 300, 99.00),
    ("Jazz Under the Stars",   "Music",      "New Orleans, LA",     29.9511, -90.0715, 150, 15.00),
    ("Food Festival 2026",     "Food & Drink","Austin, TX",         30.2672, -97.7431, 800, 10.00),
    ("Startup Pitch Night",    "Business",   "Seattle, WA",         47.6062,-122.3321, 120, 0.0),
    ("Yoga & Wellness Day",    "Health",     "Miami, FL",           25.7617, -80.1918, 80,  20.00),
    ("Digital Art Exhibition", "Arts",       "Boston, MA",          42.3601, -71.0589, 200, 12.00),
    ("Gaming Tournament",      "Gaming",     "Las Vegas, NV",       36.1699,-115.1398, 400, 30.00),
    ("Python Workshop",        "Education",  "Remote (Virtual)",    None,    None,     50,  0.0),
    ("World Travel Expo",      "Travel",     "Denver, CO",          39.7392,-104.9903, 300, 5.00),
]


with flask_app.app_context():
    # Create tables
    db.create_all()

    # ── Admin user ─────────────────────────────────────────────
    admin = User.query.filter_by(email='admin@eventhub.com').first()
    if not admin:
        admin = User(username='admin', email='admin@eventhub.com', role='admin')
        admin.set_password('Admin@1234')
        db.session.add(admin)
        print("Created admin  -> admin@eventhub.com / Admin@1234")

    # ── Demo user ──────────────────────────────────────────────
    demo = User.query.filter_by(email='demo@eventhub.com').first()
    if not demo:
        demo = User(username='demo_user', email='demo@eventhub.com')
        demo.set_password('Demo@1234')
        demo.set_interests_list(['Technology', 'Music'])
        db.session.add(demo)
        print("Created user   -> demo@eventhub.com  / Demo@1234")

    db.session.commit()

    # ── Sample events ──────────────────────────────────────────
    admin = User.query.filter_by(email='admin@eventhub.com').first()
    if Event.query.count() == 0:
        now = datetime.utcnow()
        for i, (title, cat, loc, lat, lng, cap, price) in enumerate(SAMPLE_EVENTS):
            days_ahead = random.randint(2, 90)
            start = now + timedelta(days=days_ahead, hours=random.randint(9, 19))
            end   = start + timedelta(hours=random.randint(2, 8))
            ev = Event(
                title       = title,
                description = (
                    f"Join us for {title}! This is an incredible event bringing together "
                    f"the best minds in {cat}. Expect world-class speakers, hands-on sessions, "
                    f"networking opportunities, and an unforgettable experience. "
                    f"Don't miss out — spots are limited."
                ),
                category     = cat,
                location     = loc,
                latitude     = lat,
                longitude    = lng,
                date         = start,
                end_date     = end,
                capacity     = cap,
                price        = price,
                is_virtual   = (lat is None),
                organizer_id = admin.id,
            )
            db.session.add(ev)
        db.session.commit()
        print(f"Created {len(SAMPLE_EVENTS)} sample events.")
    else:
        print("Events already exist — skipping.")

    print("\nOK Database seeded successfully!")
    print("  Admin:  admin@eventhub.com  / Admin@1234")
    print("  Demo:   demo@eventhub.com   / Demo@1234")
