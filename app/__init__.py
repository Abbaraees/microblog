import logging
import os

from logging.handlers import SMTPHandler, RotatingFileHandler
from logging import Formatter

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)


if not app.debug:
    """
    Configure the mail server to send any unhandled exception that occurred
    while the application is running in production environment.
    """
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

        mailhandler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'],
            subject='Microblog Failure!',
            credentials=auth,
            secure=secure
        )
        mailhandler.setLevel(logging.ERROR)
        app.logger.addHandler(mailhandler)

    # set the directory for the logs
    if not os.path.exists('logs'):
        os.makedirs('logs')

    filehandler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    filehandler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(msg)s [in %(pathname)s:%(lineno)d]")
    )
    filehandler.setLevel(logging.INFO)
    app.logger.addHandler(filehandler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Microblog startup")





from app import routes, models, errors
