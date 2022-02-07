from datetime import datetime

from flask import (
    render_template, redirect, url_for, flash, request, g,
    current_app
    )
from flask_babel import _, get_locale
from flask_login import current_user, login_user, logout_user, login_required
from langdetect import detect, LangDetectException
from werkzeug.urls import url_parse

from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm


from app.main.models import User, Post
from app.main import bp
from app.translate import translate


@bp.before_request
def before_request():
    g.locale = str(get_locale())
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    page = request.args.get('page', 1, int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POST_PER_PAGE'], False)

    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None

    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''

        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_("Your Post is now live!"))

        return redirect(url_for('main.index'))

    return render_template('index.html', title="Home", posts=posts.items,
                           form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title="Home", posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route("/user/<username>")
def profile(username):
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, int)
    posts = Post.query.filter_by(author=user).\
        order_by(Post.timestamp.desc()).paginate(page, current_app.config['POST_PER_PAGE'], False)
    next_url = url_for('main.profile', page=posts.next_num, username=user.username) if posts.has_next else None
    prev_url = url_for('main.profile', page=posts.prev_num, username=user.username) if posts.has_prev else None

    return render_template("profile.html", user=user, form=form, posts=posts.items,
                           title="Profile", next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()

        return redirect(url_for('main.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

        return render_template('edit_profile.html', title='Edit Profile', form=form)

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>', methods=['POST'])
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
            return redirect(url_for('main.index'))

        if user == current_user:
            flash("Sorry you can not follow yourself")
            return redirect(url_for('main.index'))
        if current_user.is_following(user):
            flash(f"You are already following {username}")
            return redirect(url_for('main.profile', username=username))

        current_user.follow(user)
        db.session.commit()
        flash(_("You are now following %(username)s", username=username))
        return redirect(url_for('main.profile', username=username))

    return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"Sorry the User {username} does not exists!")
            return redirect(url_for('main.index'))

        if user == current_user:
            flash("Sorry you can not unfollow yourself")
            return redirect(url_for('main.index'))
        elif not current_user.is_following(user):
            flash(f"You did not follow {username}")

        current_user.unfollow(user)
        db.session.commit()
        flash(_("You are not following %(username)s", username=username))
        return redirect(url_for('main.profile', username=username))

    return redirect(url_for('main.index'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return {'text': translate(request.form['text'],
                              request.form['source_language'],
                              request.form['dest_language'])}
