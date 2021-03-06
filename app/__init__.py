import logging
import os

from logging.handlers import SMTPHandler, RotatingFileHandler
from logging import Formatter

from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from elasticsearch import Elasticsearch

from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l("You have to logged in before you can view this resource")
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    if os.environ.get('ELASTICSEARCH_URL'):
        app.elasticsearch = Elasticsearch(os.environ.get('ELASTICSEARCH_URL'))
    elif os.environ.get('ELASTICSEARCH_CLOUD_ID'):
        app.elasticsearch = Elasticsearch(
            cloud_id=os.environ.get('ELASTICSEARCH_CLOUD_ID'),
            basic_auth=(os.environ.get('ELASTICSEARCH_USER'), os.environ.get('ELASTICSEARCH_PASS'))
        )
    else:
        app.elasticsearch = None

    # Register extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)


    # Register Blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


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

    return app


@babel.localeselector
def localeselector():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
