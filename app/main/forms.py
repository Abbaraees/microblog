from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_babel import lazy_gettext as _l

from app.main.models import User


class EditProfileForm(FlaskForm):
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_usernme = original_username

    username = StringField(_l("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About Me"), validators=[Length(min=0, max=150)])
    submit = SubmitField(_l("Update"))

    def validate_username(self, username):
        """
        Query the database and ensure that the username does not exists
        :return:
        """
        if username.data != self.original_usernme:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(_l("Please choose another username"))


class EmptyForm(FlaskForm):
    submit = SubmitField()


class PostForm(FlaskForm):
    post = TextAreaField(_l("Say Something:"), validators=[DataRequired(), Length(1, 150)])
    submit = SubmitField(_l("Post"))


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args

        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}

        super(SearchForm, self).__init__(*args, **kwargs)

