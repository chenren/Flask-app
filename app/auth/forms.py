from flask_wtf import FlaskForm
from wtforms.validators import *
import wtforms

from ..models import User, Role


class LoginForm(FlaskForm):
    email = wtforms.StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = wtforms.PasswordField('Password', validators=[DataRequired()])
    remember_me = wtforms.BooleanField('keep me logged in')
    submit = wtforms.SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = wtforms.StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username = wtforms.StringField('Username',
                                   validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                                      message='Username must have only letters,'
                                                              ' numbers, dots or underscores')])
    password = wtforms.PasswordField('Password',
                                     validators=[DataRequired(), EqualTo('password2', message='password not match')])
    password2 = wtforms.PasswordField('Confirm password', validators=[DataRequired()])
    submit = wtforms.SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise(ValidationError('Email already registered.'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise (ValidationError('Username already in use.'))


class ChangePasswordForm(FlaskForm):
    old_pw = wtforms.PasswordField('Old password', validators=[DataRequired()])
    new_pw = wtforms.PasswordField('New password', validators=[DataRequired(), EqualTo('new_pw2', 'password not match')])
    new_pw2 = wtforms.PasswordField('Confirm password', validators=[DataRequired()])
    submit = wtforms.SubmitField('Confirm')


class ChangeEmailForm(FlaskForm):
    email = wtforms.StringField('New email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = wtforms.PasswordField('Confirm password', validators=[DataRequired()])
    submit = wtforms.SubmitField('Confirm')


class ResetPasswordRequestForm(FlaskForm):
    email = wtforms.StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    submit = wtforms.SubmitField('Sent')


class ResetPasswordForm(FlaskForm):
    password = wtforms.PasswordField('Password',
                                     validators=[DataRequired(), EqualTo('password2', message='password not match')])
    password2 = wtforms.PasswordField('Confirm password', validators=[DataRequired()])
    submit = wtforms.SubmitField('Confirm')


class EditProfileForm(FlaskForm):
    name = wtforms.StringField('Real name', validators=[Length(0, 64)])
    location = wtforms.StringField('Location', validators=[Length(0, 64)])
    about_me = wtforms.StringField('About me')
    submit = wtforms.SubmitField('Save')


class EditProfileAdminForm(FlaskForm):
    email = wtforms.StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username = wtforms.StringField('Username',
                                   validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                                                      message='Username must have only letters,'
                                                              ' numbers, dots or underscores')])
    confirmed = wtforms.BooleanField('Confirmed')
    role = wtforms.SelectField('Role', coerce=int)
    name = wtforms.StringField('Real name', validators=[Length(0, 64)])
    location = wtforms.StringField('Location', validators=[Length(0, 64)])
    about_me = wtforms.TextAreaField('About me')
    submit = wtforms.SubmitField('Save')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if self.email.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise(ValidationError('Email already registered.'))

    def validate_username(self, field):
        if self.username.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise (ValidationError('Username already in use.'))

    def init_field(self):
        if self.user:
            self.email.data = self.user.email
            self.username.data = self.user.username
            self.confirmed.data = self.user.confirmed
            self.role.data = self.user.role.id
            self.name.data = self.user.name
            self.location.data = self.user.location
            self.about_me.data = self.user.about_me


class SearchUserForm(FlaskForm):
    userid = wtforms.SelectField('User', coerce=int)
    submit = wtforms.SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(SearchUserForm, self).__init__(*args, **kwargs)
        self.userid.choices = [(user.id, '{} <{}>'.format(user.username, user.email))
                               for user in User.query.order_by(User.username).all()]
