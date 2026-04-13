import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.forms import LoginForm, SignupForm, ProfileForm

auth_bp = Blueprint('auth', __name__)


def _save_file(file_obj, upload_folder):
    """Save an uploaded file with a unique name; return the filename."""
    original  = secure_filename(file_obj.filename)
    unique    = f"{os.urandom(8).hex()}_{original}"
    file_obj.save(os.path.join(upload_folder, unique))
    return unique


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Welcome to EventHub.', 'success')
        return redirect(url_for('main.home'))

    return render_template('auth/signup.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Ensure uniqueness excluding current user
        clash = User.query.filter_by(username=form.username.data).first()
        if clash and clash.id != current_user.id:
            flash('Username already taken.', 'danger')
        else:
            current_user.username = form.username.data
            current_user.bio      = form.bio.data or ''
            if form.interests.data:
                current_user.set_interests_list([form.interests.data])

            if form.avatar.data and form.avatar.data.filename:
                fname = _save_file(form.avatar.data,
                                   current_app.config['UPLOAD_FOLDER'])
                current_user.avatar = fname

            db.session.commit()
            flash('Profile updated!', 'success')
            return redirect(url_for('auth.profile'))

    # Show user's registered events on the profile page
    from app.models.ticket import Ticket
    from app.models.event  import Event
    from datetime import datetime
    now     = datetime.utcnow()
    tickets = (Ticket.query
               .filter_by(user_id=current_user.id, status='active')
               .join(Event).order_by(Event.date.asc()).all())

    return render_template('auth/profile.html', form=form,
                           tickets=tickets, now=now)
