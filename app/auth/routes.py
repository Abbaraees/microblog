from flask import render_template, redirect, url_for, request, flash
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth import bp
from app.auth.email import send_reset_password_email
from app.auth.forms import LoginForm, RegistrationForm, PasswordResetForm, PasswordResetRequestForm
from app.main.models import db, User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log the user into the application by getting his username
    and password from the login form

    :return: redirect
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid Username or Password"))
            return render_template('auth/login.html', title="Sign In", form=form)

        login_user(user, remember=form.remember_me.data)

        next_url = request.args.get('next')
        if not next_url or url_parse(next_url).netloc != '':
            return redirect(url_for('main.index'))

        return redirect(next_url)

    return render_template('auth/login.html', title="Sign In", form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(_("Congratulations you are now a registered user"))
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title="Register", form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)

        flash(_("Check your Email for instructions to reset your password"))
        return redirect(url_for('auth.login'))

    return render_template('auth/password_reset_request.html', title='Password Reset Request', form=form)


@bp.route('/password_reset/<token>', methods=['POST', 'GET'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()

    user = User.verify_password_reset_token(token)
    if not user:
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        user.set_password(form.password1.data)
        db.session.commit()
        flash(_("Your password has been reset successfully!"))

        return redirect(url_for('auth.login'))

    return render_template('auth/password_reset.html', title='Password Reset', form=form)
