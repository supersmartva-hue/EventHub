import os
from datetime import datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.event        import Event, CATEGORIES
from app.models.ticket       import Ticket
from app.models.comment      import Comment
from app.models.notification import Notification
from app.forms import EventForm, CommentForm

events_bp = Blueprint('events', __name__)


def _save_image(file_obj, upload_folder):
    original = secure_filename(file_obj.filename)
    unique   = f"{os.urandom(8).hex()}_{original}"
    file_obj.save(os.path.join(upload_folder, unique))
    return unique


# ── List all events ───────────────────────────────────────────
@events_bp.route('/')
def list_events():
    page     = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    q        = request.args.get('q', '')
    sort     = request.args.get('sort', 'date')   # date | price
    now      = datetime.utcnow()

    base = Event.query.filter(Event.is_published == True, Event.date > now)

    if category:
        base = base.filter(Event.category == category)
    if q:
        base = base.filter(Event.title.ilike(f'%{q}%') |
                           Event.location.ilike(f'%{q}%'))
    if sort == 'price':
        base = base.order_by(Event.price.asc())
    else:
        base = base.order_by(Event.date.asc())

    events = base.paginate(page=page,
                           per_page=current_app.config['EVENTS_PER_PAGE'],
                           error_out=False)

    return render_template('events/list.html',
                           events=events,
                           categories=CATEGORIES,
                           selected_category=category,
                           q=q, sort=sort)


# ── Event detail ──────────────────────────────────────────────
@events_bp.route('/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)

    user_ticket = None
    if current_user.is_authenticated:
        user_ticket = Ticket.query.filter_by(
            user_id=current_user.id,
            event_id=event_id,
            status='active'
        ).first()

    comments     = (Comment.query
                    .filter_by(event_id=event_id)
                    .order_by(Comment.created_at.desc())
                    .all())
    comment_form = CommentForm()

    similar = (Event.query
               .filter(Event.category == event.category,
                       Event.id != event_id,
                       Event.date > datetime.utcnow(),
                       Event.is_published == True)
               .limit(3).all())

    return render_template('events/detail.html',
                           event=event,
                           user_ticket=user_ticket,
                           comments=comments,
                           comment_form=comment_form,
                           similar=similar)


# ── Create event ──────────────────────────────────────────────
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title        = form.title.data,
            description  = form.description.data,
            category     = form.category.data,
            location     = form.location.data,
            latitude     = form.latitude.data,
            longitude    = form.longitude.data,
            date         = form.date.data,
            end_date     = form.end_date.data,
            capacity     = form.capacity.data,
            price        = form.price.data or 0.0,
            is_virtual   = form.is_virtual.data,
            meet_link    = form.meet_link.data or '',
            organizer_id = current_user.id,
        )
        if form.image.data and form.image.data.filename:
            event.image = _save_image(form.image.data,
                                      current_app.config['UPLOAD_FOLDER'])

        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('events/create.html', form=form)


# ── Edit event ────────────────────────────────────────────────
@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    event = Event.query.get_or_404(event_id)

    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.title       = form.title.data
        event.description = form.description.data
        event.category    = form.category.data
        event.location    = form.location.data
        event.latitude    = form.latitude.data
        event.longitude   = form.longitude.data
        event.date        = form.date.data
        event.end_date    = form.end_date.data
        event.capacity    = form.capacity.data
        event.price       = form.price.data or 0.0
        event.is_virtual  = form.is_virtual.data
        event.meet_link   = form.meet_link.data or ''

        if form.image.data and form.image.data.filename:
            event.image = _save_image(form.image.data,
                                      current_app.config['UPLOAD_FOLDER'])

        # Notify all registered attendees of the update
        registrants = [t.user for t in event.tickets.filter_by(status='active').all()]
        for u in registrants:
            if u.id != current_user.id:
                db.session.add(Notification(
                    user_id=u.id,
                    message=f'Event "{event.title}" has been updated.',
                    link=url_for('events.detail', event_id=event.id)
                ))

        db.session.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('events/edit.html', form=form, event=event)


# ── Delete event ──────────────────────────────────────────────
@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('events.list_events'))


# ── Add comment ───────────────────────────────────────────────
@events_bp.route('/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    event = Event.query.get_or_404(event_id)
    form  = CommentForm()

    if form.validate_on_submit():
        db.session.add(Comment(
            body=form.body.data,
            user_id=current_user.id,
            event_id=event_id
        ))
        # Notify organiser (unless they commented on their own event)
        if event.organizer_id != current_user.id:
            db.session.add(Notification(
                user_id=event.organizer_id,
                message=f'{current_user.username} commented on "{event.title}".',
                link=url_for('events.detail', event_id=event_id)
            ))
        db.session.commit()
        flash('Comment posted!', 'success')

    return redirect(url_for('events.detail', event_id=event_id))


# ── Calendar view ─────────────────────────────────────────────
@events_bp.route('/calendar')
def calendar():
    return render_template('events/calendar.html')
