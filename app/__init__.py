import decimal
import os
from config import Config
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from logging.handlers import SMTPHandler, RotatingFileHandler
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()

# logging to determine sqlalchemy query times
# logging.basicConfig()
# logger = logging.getLogger('sqlalchemy.engine')
# logger.setLevel(logging.DEBUG)


# @event.listens_for(Engine, "before_cursor_execute")
# def before_cursor_execute(conn, cursor, statement,
#                         parameters, context, executemany):
#     conn.info.setdefault('query_start_time', []).append(time.time())
#     logger.debug("Start Query: %s", statement)
#
#
# @event.listens_for(Engine, "after_cursor_execute")
# def after_cursor_execute(conn, cursor, statement,
#                         parameters, context, executemany):
#     total = time.time() - conn.info['query_start_time'].pop(-1)
#     logger.debug("Query Complete!")
#     logger.debug("Total Time: %f", total)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .views.charge import charge_bp
    app.register_blueprint(charge_bp, url_prefix='/views')

    from .views.doc_ import doc_bp
    app.register_blueprint(doc_bp, url_prefix='/views')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .views.filter import filter_bp
    app.register_blueprint(filter_bp, url_prefix='/views')

    from .views.form_letter import form_letter_bp
    app.register_blueprint(form_letter_bp, url_prefix='/views')

    from .views.headrent import headrent_bp
    app.register_blueprint(headrent_bp, url_prefix='/views')

    from .views.income import  income_bp
    app.register_blueprint(income_bp, url_prefix='/views')

    from .views.lease import lease_bp
    app.register_blueprint(lease_bp, url_prefix='/views')

    from .views.loan import loan_bp
    app.register_blueprint(loan_bp, url_prefix='/views')

    from .views.mail import mail_bp
    app.register_blueprint(mail_bp, url_prefix='/views')

    from .views.money import money_bp
    app.register_blueprint(money_bp, url_prefix='/views')

    from .views.payrequest import pr_bp
    app.register_blueprint(pr_bp, url_prefix='/views')

    from .views.rental import rental_bp
    app.register_blueprint(rental_bp, url_prefix='/views')

    from .views.rent import rent_bp
    app.register_blueprint(rent_bp, url_prefix='/views')

    from .views.utility import util_bp
    app.register_blueprint(util_bp)

    from .views.backup import backup_bp
    app.register_blueprint(backup_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='MJinn Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/mjinn.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Mjinn startup')

    return app


from app import models
