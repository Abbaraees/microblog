import os

from dotenv import load_dotenv

load_dotenv('.env')

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    ADMINS = ['abbaraees@gmail.com']
    POST_PER_PAGE = 10
    LANGUAGES = ['en', 'ha']
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    ELASTICSEARCH_CLOUD_ID = os.environ.get("ELASTICSEARCH_CLOUD_ID")
    ELASTICSEARCH_USER = os.environ.get("ELASTICSEARCH_USER_")
    ELASTICSEARCH_PASS = os.environ.get("ELASTICSEARCH_PASS")
