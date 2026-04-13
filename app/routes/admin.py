from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models.user         import User
from app.models.event        import Event
from app.models.ticket       import Ticket
from app.utils.decorators    import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    now = datetime.utcnow()

    # ── KPI metrics ───────────────────────────────────────────
    total_events   = Event.query.count()
    total_users    = User.query.count()
    total_tickets  = Ticket.query.filter_by(status='active').count()
    upcoming_count = Event.query.filter(Event.date > now).count()

    # Total revenue = sum of each ticket's event price
    revenue = (db.session.query(func.sum(Event.price))
               .join(Ticket, Ticket.event_id == Event.id)
               .filter(Ticket.status == 'active')
               .scalar()) or 0.0

    # ── Recent activity ────────────────────────────────────────
    recent_events = (Event.query.order_by(Event.created_at.desc()).limit(5).all())
    recent_users  = (User.query.order_by(User.created_at.desc()).limit(5).all())

    # ── Chart data: events per category ───────────────────────
    category_rows = (db.session.query(Event.category, func.count(Event.id))
                     .group_by(Event.category).all())
    category_data = [{'label': row[0], 'count': row[1]} for row in category_rows]

    # ── Chart data: daily registrations for last 7 days ───────
    reg_data = []
    for i in range(6, -1, -1):
        day   = now - timedelta(days=i)
        start = day.replace(hour=0,  minute=0,  second=0,  microsecond=0)
        end   = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        count = (Ticket.query
                 .filter(Ticket.registered_at.between(start, end),
                         Ticket.status == 'active')
                 .count())
        reg_data.append({'day': day.strftime('%a'), 'count': count})

    return render_template('admin/dashboard.html',
                           total_events=total_events,
                           total_users=total_users,
                           total_tickets=total_tickets,
                           upcoming_count=upcoming_count,
                           revenue=revenue,
                           recent_events=recent_events,
                           recent_users=recent_users,
                           category_data=category_data,
                           reg_data=reg_data)


@admin_bp.route('/events')
@login_required
@admin_required
def events():
    page   = request.args.get('page', 1, type=int)
    events = (Event.query.order_by(Event.created_at.desc())
              .paginate(page=page, per_page=15, error_out=False))
    return render_template('admin/events.html', events=events)


@admin_bp.route('/events/<int:event_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_event(event_id):
    event = Event.query.get_or_404(event_id)
    event.is_published = not event.is_published
    db.session.commit()
    flash(f'Event {"published" if event.is_published else "unpublished"}.', 'success')
    return redirect(url_for('admin.events'))


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('admin.events'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page  = request.args.get('page', 1, type=int)
    users = (User.query.order_by(User.created_at.desc())
             .paginate(page=page, per_page=15, error_out=False))
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot change your own admin role.', 'danger')
    else:
        user.role = 'user' if user.is_admin else 'admin'
        db.session.commit()
        flash(f'{user.username} is now a {user.role}.', 'success')
    return redirect(url_for('admin.users'))
