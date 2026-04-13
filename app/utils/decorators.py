from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """
    Route decorator — only allows admin users.
    Usage:  @admin_required  (place below @login_required)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
