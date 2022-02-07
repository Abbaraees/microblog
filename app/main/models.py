from time import time
from datetime import datetime
from hashlib import md5

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

import jwt

from app import db, login


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(20))

    def __repr__(self):
        return f"<Post '{self.body}'>"
