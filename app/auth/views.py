from flask import render_template, redirect, request, url_for, flash
import flask_login
from flask_login import login_required, current_user
from . import auth_blueprint
from .forms import *
from .. import db
from ..email import send_email
from ..decorators import admin_required



@auth_blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            flask_login.login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        else:
            flash('Invalid email or password')
    return render_template('auth/login.html', form=form)


@auth_blueprint.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    flash('you have been logged out')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/secret')
@login_required
def secret():
    return 'secret page, please login in.'


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        send_email(user.email, '[TEST]Confirm Your Account', 'auth/email/confirm', token=token, user=user)
        flash('You can now login.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth_blueprint.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    send_email(current_user.email, '[TEST]Confirm Your Account', 'auth/email/confirm', token=token, user=current_user)
    flash('A new confirmation has been sent to your email.')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/confirm/<token>')
@login_required
def confirm(token):
    data = {}
    if current_user.confirm_token(token, token_data=data):
        current_user.confirmed = True
        if 'email' in data:
            current_user.email = data.get('email')
        db.session.add(current_user)
        db.session.commit()
        flash('confirmed.')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth_blueprint.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', current_user=current_user)


@auth_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_pw.data):
            flash('Old password is not correct.')
        elif form.old_pw.data == form.new_pw.data:
            flash('New password is the same as the old.')
        else:
            current_user.password = form.new_pw.data
            db.session.add(current_user)
            db.session.commit()
            flash('Password change succeed.')
    return render_template('auth/change_password.html', form=form)


@auth_blueprint.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            if current_user.email == form.email.data:
                flash('New email is the same as the old.')
            else:
                token = current_user.generate_token(extra_data={'email': form.email.data})
                send_email(form.email.data, '[TEST]Change Email', 'auth/email/confirm',
                           token=token, user=current_user)
                flash('A confirm email has been sent to your email.')
        else:
            flash('Password error.')
    return render_template('auth/change_email.html', form=form)


@auth_blueprint.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('Current email has not been registered.')
        else:
            token = user.generate_token(confirm_list=['id', 'email'])
            send_email(form.email.data, '[TEST]Reset Your Account', 'auth/email/reset_password', token=token)
            flash('A reset email has been sent to your email.')
    return render_template('auth/reset_password.html', form=form)


@auth_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    data = {}
    if form.validate_on_submit():
        if User.confirm_token(token, ['id', 'email'], data):
            user = User.query.filter_by(id=data.get('id')).first()
            if user and not user.verify_password(form.password.data):
                user.password = form.password.data
                db.session.add(user)
                db.session.commit()
                flash('Password has been rested.')
                return redirect(url_for('auth.login'))
            else:
                flash('New password is the same as the old.')
        else:
            flash('The confirmation link is invalid or has expired.')
    return render_template('auth/reset_password.html', form=form)


@auth_blueprint.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Profile update')
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('/auth/edit_profile.html', form=form)


@auth_blueprint.route('/edit_profile_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin():
    search_form = SearchUserForm()
    # edit_form = None
    if search_form.validate():
        return redirect(url_for('auth.edit_profile_admin_with_id', userid=search_form.userid.data))
    search_form.userid.data = current_user.id
    return render_template('/auth/edit_profile_admin.html', search_form=search_form)


@auth_blueprint.route('/edit_profile_admin/<int:userid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin_with_id(userid):
    user = User.query.get_or_404(userid)
    search_form = SearchUserForm()
    edit_form = EditProfileAdminForm(user)
    if search_form.validate_on_submit():
        return redirect(url_for('auth.edit_profile_admin_with_id', userid=search_form.userid.data))
    elif edit_form.validate_on_submit():
        user.email = edit_form.email.data
        user.username = edit_form.username.data
        user.confirmed = edit_form.confirmed.data
        user.role = Role.query.get(edit_form.role.data)
        user.name = edit_form.name.data
        user.location = edit_form.location.data
        user.about_me = edit_form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('profile updated.')
    else:
        edit_form.init_field()
    search_form.userid.data = userid
    return render_template('/auth/edit_profile_admin.html', search_form=search_form, edit_form=edit_form)
