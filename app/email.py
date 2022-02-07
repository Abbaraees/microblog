from threading import Thread

from flask import render_template, current_app
from flask_mail import Message

from app import  mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body, text_body):
    msg = Message(subject=subject, recipients=recipients, sender=sender)
    msg.html = html_body
    msg.body = text_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
