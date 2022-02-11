from time import time
from datetime import datetime
from hashlib import md5

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

import jwt

from app import db, login
from app.search import add_to_index, query_index, remove_from_index


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class SearchableMixin(object):
    """
    when attached to a model, will give it the ability to automatically
    manage an associated full-text index
    """
    @classmethod
    def search(cls, expression, page, per_page):
        """
        Query the database and select all posts that that match
        the given expression
        """

        # get the ids for the posts that match the given expression
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0).all(), 0

        when = []

        for i in range(len(ids)):
            when.append((ids[i], i))

        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total


    @classmethod
    def before_commit(cls, session):
        """
        record all the new changes in the session before commit
        """
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }


    @classmethod
    def after_commit(cls, session):
        """
        apply the new changes to the elasticsearch index after commit.
        """
        if session._changes['add']:
            for obj in session._changes['add']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(cls.__tablename__, obj)

        if session._changes['update']:
            for obj in session._changes['update']:
                if isinstance(obj, SearchableMixin):
                    add_to_index(cls.__tablename__, obj)

        if session._changes['delete']:
            for obj in session._changes['delete']:
                if isinstance(obj, SearchableMixin):
                    remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(150))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User',
        secondary='followers',
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<User '{self.username}'>"

    def set_password(self, password):
        """
        hash the given password and store the hash value in the password_hash column
        :param password:
        :return: None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify whether the given password is thesame as the hash_password
        :param password:
        :return: bool
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        hexdigest = md5(self.email.lower().encode('utf-8')).hexdigest()
        url = f"https://www.gravatar.com/avatar/{hexdigest}?s={size}&d=identicon"
        return url

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)

        # Get user's owned posts
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_password_reset_token(self):
        payload = {'reset_password': self.id, 'exp': time() + 600}
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

        return token

    @staticmethod
    def verify_password_reset_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], 'HS256')['reset_password']
        except:
            return

        return User.query.get(user_id)


class Post(db.Model, SearchableMixin):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(20))

    def __repr__(self):
        return f"<Post '{self.body}'>"
