from flask import current_app
from flask_mail import Message
from app import mail


def send_registration_confirmation(user, event, ticket):
    """Email a booking confirmation to the user."""
    try:
        msg = Message(
            subject=f"You're registered for {event.title}!",
            recipients=[user.email]
        )
        msg.body = f"""Hi {user.username},

You have successfully registered for:

  {event.title}
  Date:     {event.date.strftime('%B %d, %Y at %I:%M %p')}
  Location: {event.location}
  Ticket:   {ticket.ticket_code}

Show your QR code at the entrance.

See you there!
— The EventHub Team
"""
        mail.send(msg)
    except Exception as exc:
        # Email failure must never break the registration flow
        current_app.logger.warning(f"Email send failed: {exc}")


def send_event_update_notification(users, event, update_message):
    """Notify a list of users that an event they registered for was updated."""
    for user in users:
        try:
            msg = Message(
                subject=f"Update on: {event.title}",
                recipients=[user.email]
            )
            msg.body = (
                f"Hi {user.username},\n\n"
                f"{update_message}\n\n"
                f"Event: {event.title}\n"
                f"Date:  {event.date.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                f"— EventHub Team"
            )
            mail.send(msg)
        except Exception as exc:
            current_app.logger.warning(f"Email failed for {user.email}: {exc}")
