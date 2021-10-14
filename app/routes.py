from datetime import datetime

from flask import (
    render_template, redirect, url_for, flash, request
    )
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {"author": {"username": "Abba Raees"}, "post": "Hello and Welcome to my Blog"},
        {"author": {"username": "Muhammad Lawal"}, "post": "Never Let your anger controls you"},
        {"author": {"username": "Umar S Alkalee"}, "post": "Eat, Code, Sleep"},
        {"author": {"username": "Abba Raees"}, "post": "Hello and Welcome to my Blog"},
    ]

    return render_template('index.html', title="Home", posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log the user into the application by getting his username
    and password from the login form

    :return: redirect
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Username or Password")
            return render_template('login.html', title="Sign In", form=form)

        login_user(user, remember=form.remember_me.data)

        next_url = request.args.get('next')
        if not next_url or url_parse(next_url).netloc != '':
            return redirect(url_for('index'))

        return redirect(next_url)

    return render_template('login.html', title="Sign In", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Congratulations you are now a registered user")
        return redirect(url_for('login'))

    return render_template('register.html', title="Register", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/user/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {"author": current_user, "body": "Test Post #1"},
        {"author": current_user, "body": "Test Post #2"}
    ]

    return render_template("profile.html", user=user, posts=posts, title="Profile")


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        return redirect(url_for('profile', username=current_user.username))
    else:
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

        return render_template('edit_profile.html', title='Edit Profile', form=form)
