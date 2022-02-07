from flask import render_template, current_app

from app.email import send_email


def send_reset_password_email(user):
    html_body = render_template('email/reset_password.html', user=user)
    text_body = render_template('email/reset_password.txt', user=user)
    send_email(
        subject='[Microblog] Reset Password',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        html_body=html_body,
        text_body=text_body
    )
