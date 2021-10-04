from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

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
