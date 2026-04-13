from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models.event        import Event
from app.models.ticket       import Ticket
from app.models.notification import Notification
from app.utils.qr_generator  import generate_ticket_qr

tickets_bp = Blueprint('tickets', __name__)


@tickets_bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register(event_id):
    event = Event.query.get_or_404(event_id)

    if event.is_past:
        flash('This event has already passed.', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    already = Ticket.query.filter_by(
        user_id=current_user.id, event_id=event_id, status='active'
    ).first()
    if already:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('events.detail', event_id=event_id))

    if event.is_full:
        flash('Sorry, this event is fully booked.', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    ticket = Ticket(user_id=current_user.id, event_id=event_id)
    db.session.add(ticket)
    db.session.flush()   # Populate ticket.id before we need it for the QR

    # Generate QR code image
    try:
        qr_file = generate_ticket_qr(ticket.ticket_code, ticket.id)
        ticket.qr_code_path = qr_file
    except Exception:
        pass   # Never block registration due to QR failure

    # Notify the organiser
    db.session.add(Notification(
        user_id=event.organizer_id,
        message=f'{current_user.username} registered for "{event.title}".',
        link=url_for('events.detail', event_id=event_id)
    ))
    db.session.commit()

    flash(f'Registered for {event.title}! Your QR ticket is ready.', 'success')
    return redirect(url_for('tickets.my_tickets'))


@tickets_bp.route('/my-tickets')
@login_required
def my_tickets():
    now     = datetime.utcnow()
    tickets = (Ticket.query
               .filter_by(user_id=current_user.id, status='active')
               .join(Event)
               .order_by(Event.date.asc())
               .all())

    upcoming = [t for t in tickets if t.event.date > now]
    past     = [t for t in tickets if t.event.date <= now]

    return render_template('tickets/my_tickets.html',
                           upcoming=upcoming, past=past, now=now)


@tickets_bp.route('/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('tickets/ticket_detail.html', ticket=ticket)


@tickets_bp.route('/cancel/<int:ticket_id>', methods=['POST'])
@login_required
def cancel(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id:
        abort(403)

    ticket.status = 'cancelled'
    db.session.commit()
    flash('Registration cancelled.', 'info')
    return redirect(url_for('tickets.my_tickets'))
