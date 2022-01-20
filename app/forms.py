from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_babel import lazy_gettext as _l

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember me"))
    submit = SubmitField(_l("Login"))


class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(_l("New Password"), validators=[DataRequired()])
    password2 = PasswordField(_l("Repeat Password"), validators=[DataRequired(),
                                                             EqualTo('password')])
    submit = SubmitField(_l("Register"))

    def validate_username(self, username):
        """
        Query the database and ensure that the username does not exists
        :return:
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l("Please choose another username"))

    def validate_email(self, email):
        """
        Query the database and ensure that the email does not exists
        :return:
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l("Please choose another email"))


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


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class PasswordResetForm(FlaskForm):
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField("Reset")
