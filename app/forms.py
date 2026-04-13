from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, BooleanField, TextAreaField,
                     SelectField, FloatField, IntegerField, DateTimeLocalField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                Optional, NumberRange, ValidationError)
from app.models.event import CATEGORIES


class LoginForm(FlaskForm):
    email    = StringField('Email',    validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class SignupForm(FlaskForm):
    username         = StringField('Username',
                                   validators=[DataRequired(), Length(3, 64)])
    email            = StringField('Email',
                                   validators=[DataRequired(), Email()])
    password         = PasswordField('Password',
                                     validators=[DataRequired(), Length(8, 128)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Passwords must match.')])

    def validate_username(self, field):
        from app.models.user import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        from app.models.user import User
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')


class ProfileForm(FlaskForm):
    username  = StringField('Username',   validators=[DataRequired(), Length(3, 64)])
    bio       = TextAreaField('Bio',      validators=[Optional(), Length(max=500)])
    interests = SelectField('Primary Interest',
                            choices=[('', 'Select an interest...')] +
                                    [(c, c) for c in CATEGORIES],
                            validators=[Optional()])
    avatar    = FileField('Profile Picture',
                          validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'],
                                                  'Images only!')])


class EventForm(FlaskForm):
    title       = StringField('Event Title',
                              validators=[DataRequired(), Length(3, 200)])
    description = TextAreaField('Description',
                                validators=[DataRequired(), Length(min=20)])
    category    = SelectField('Category',
                              choices=[(c, c) for c in CATEGORIES],
                              validators=[DataRequired()])
    location    = StringField('Location / Venue',
                              validators=[DataRequired()])
    latitude    = FloatField('Latitude',  validators=[Optional()])
    longitude   = FloatField('Longitude', validators=[Optional()])
    date        = DateTimeLocalField('Start Date & Time',
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[DataRequired()])
    end_date    = DateTimeLocalField('End Date & Time',
                                    format='%Y-%m-%dT%H:%M',
                                    validators=[Optional()])
    capacity    = IntegerField('Capacity',
                               validators=[DataRequired(), NumberRange(min=1, max=100000)])
    price       = FloatField('Ticket Price ($)',
                             validators=[Optional(), NumberRange(min=0)])
    is_virtual  = BooleanField('This is a virtual event')
    meet_link   = StringField('Meeting Link (Zoom / Google Meet)',
                              validators=[Optional()])
    image       = FileField('Event Cover Image',
                            validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'],
                                                    'Images only!')])


class CommentForm(FlaskForm):
    body = TextAreaField('Write a comment…',
                         validators=[DataRequired(), Length(min=2, max=1000)])
