import os
from datetime import datetime
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some key'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASK_MAIL_SENDER = MAIL_USERNAME
    FLASK_ADMIN = MAIL_USERNAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQL_URL = 'mysql+mysqlconnector://{user}:{password}@{host}/{database}'
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    SSL_REDIRECT = False

    FLASKY_POSTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DB_CONFIG = {'host': 'localhost',
                 'user': Config.DB_USERNAME,
                 'password': Config.DB_PASSWORD,
                 'database': 'Flasky'}
    SQLALCHEMY_DATABASE_URI = Config.MYSQL_URL.format(**DB_CONFIG)


class TestingConfig(Config):
    TESTING = True
    DB_CONFIG = {'host': 'localhost',
                 'user': Config.DB_USERNAME,
                 'password': Config.DB_PASSWORD,
                 'database': 'TEST'}
    SQLALCHEMY_DATABASE_URI = Config.MYSQL_URL.format(**DB_CONFIG)


class ProductionConfig(Config):
    DB_CONFIG = {'host': 'localhost',
                 'user': Config.DB_USERNAME,
                 'password': Config.DB_PASSWORD,
                 'database': 'Flasky'}
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or Config.MYSQL_URL.format(**DB_CONFIG)

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASK_MAIL_SENDER,
            toaddrs=[cls.FLASK_ADMIN],
            subject='[Test]Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    ProductionConfig.SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        super().init_app(app)

        import logging
        file_handler = logging.StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig
}
