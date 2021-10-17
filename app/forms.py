from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("New Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(),
                                                             EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        """
        Query the database and ensure that the username does not exists
        :return:
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Please choose another username")

    def validate_email(self, email):
        """
        Query the database and ensure that the email does not exists
        :return:
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Please choose another email")


class EditProfileForm(FlaskForm):
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_usernme = original_username

    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About Me", validators=[Length(min=0, max=150)])
    submit = SubmitField("Update")

    def validate_username(self, username):
        """
        Query the database and ensure that the username does not exists
        :return:
        """
        if username.data != self.original_usernme:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Please choose another username")


class EmptyForm(FlaskForm):
    submit = SubmitField()
