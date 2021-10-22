from threading import Thread

from flask import render_template
from flask_mail import Message

from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body, text_body):
    msg = Message(subject=subject, recipients=recipients, sender=sender)
    msg.html = html_body
    msg.body = text_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_reset_password_email(user):
    html_body = render_template('email/reset_password.html', user=user)
    text_body = render_template('email/reset_password.txt', user=user)
    send_email(
        subject='[Microblog] Reset Password',
        sender=app.config['ADMINS'][0],
        recipients=[user.email],
        html_body=html_body,
        text_body=text_body
    )
