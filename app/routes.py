from datetime import datetime

from flask import (
    render_template, redirect, url_for, flash, request
    )
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import (
    LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm,
    PasswordResetRequestForm, PasswordResetForm
)
from app.models import User, Post
from app.email import send_reset_password_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    page = request.args.get('page', 1, int)
    posts = current_user.followed_posts().paginate(page, app.config['POST_PER_PAGE'], False)

    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your Post is now live!")

        return redirect(url_for('index'))

    return render_template('index.html', title="Home", posts=posts.items,
                           form=form, next_url=next_url, prev_url=prev_url)


@app.route('/explore')
def explore():
    page = request.args.get('page', 1, int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title="Home", posts=posts.items, next_url=next_url, prev_url=prev_url)


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
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, int)
    posts = Post.query.filter_by(author=user).\
        order_by(Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('profile', page=posts.next_num, username=user.username) if posts.has_next else None
    prev_url = url_for('profile', page=posts.prev_num, username=user.username) if posts.has_prev else None

    return render_template("profile.html", user=user, form=form, posts=posts.items,
                           title="Profile", next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()

        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

        return render_template('edit_profile.html', title='Edit Profile', form=form)

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """
    Follow a user

    :param username:
    :return redirect:
    """
    form = EmptyForm()

    # Verify that the csrf_token is valid
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"Sorry the User {username} does not exists!")
            return redirect(url_for('index'))

        if user == current_user:
            flash("Sorry you can not follow yourself")
            return redirect(url_for('index'))
        if current_user.is_following(user):
            flash(f"You are already following {username}")
            return redirect(url_for('profile', username=username))

        current_user.follow(user)
        db.session.commit()
        flash(f"You are now following {username}")
        return redirect(url_for("profile", username=username))

    return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"Sorry the User {username} does not exists!")
            return redirect(url_for('index'))

        if user == current_user:
            flash("Sorry you can not unfollow yourself")
            return redirect(url_for('index'))
        elif not current_user.is_following(user):
            flash(f"You did not follow {username}")

        current_user.unfollow(user)
        db.session.commit()
        flash(f"You are not following {username}")
        return redirect(url_for('profile', username=username))

    return redirect(url_for('index'))


@app.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_password_email(user)

        flash("Check your Email for instructions to reset your password")
        return redirect(url_for('login'))

    return render_template('password_reset_request.html', title='Password Reset Request', form=form)


@app.route('/password_reset/<token>', methods=['POST', 'GET'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswordResetForm()

    if form.validate_on_submit():
        user = User.verify_password_reset_token(token)
        if not user:
            return redirect(url_for('index'))

        user.set_password(form.password1.data)
        db.session.commit()
        flash("Your password has been reset successfully!")

        return redirect(url_for('login'))

    return render_template('password_reset.html', title='Password Reset', form=form)
