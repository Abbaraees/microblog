from flask import (
    render_template, redirect, url_for, flash
    )

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {"username": "Abba Raees"}
    posts = [
        {"author": {"username": "Abba Raees"}, "post": "Hello and Welcome to my Blog"},
        {"author": {"username": "Muhammad Lawal"}, "post": "Never Let your anger controls you"},
        {"author": {"username": "Umar S Alkalee"}, "post": "Eat, Code, Sleep"},
        {"author": {"username": "Abba Raees"}, "post": "Hello and Welcome to my Blog"},
    ]

    return render_template('index.html', title="Home", user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Login requested for username: {form.username.data}. \
                                    remember me: {form.remember_me.data}")
        return redirect(url_for('index'))

    return render_template('login.html', title="Sign In", form=form)
