import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from .views.agent import ag_bp
    app.register_blueprint(ag_bp, url_prefix='/views')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .views.charge import ch_bp
    app.register_blueprint(ch_bp, url_prefix='/views')

    from .views.doc_object import do_bp
    app.register_blueprint(do_bp, url_prefix='/views')

    from .views.email_account import em_bp
    app.register_blueprint(em_bp, url_prefix='/views')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .views.form_letter import fo_bp
    app.register_blueprint(fo_bp, url_prefix='/views')

    from .views.headrent import hr_bp
    app.register_blueprint(hr_bp, url_prefix='/views')

    from .views.home import ho_bp
    app.register_blueprint(ho_bp, url_prefix='/')

    from .views.income_object import  io_bp
    app.register_blueprint(io_bp, url_prefix='/views')

    from .views.landlord import la_bp
    app.register_blueprint(la_bp, url_prefix='/views')

    from .views.lease import le_bp
    app.register_blueprint(le_bp, url_prefix='/views')

    from .views.loan import lo_bp
    app.register_blueprint(lo_bp, url_prefix='/views')

    from .views.money import mo_bp
    app.register_blueprint(mo_bp, url_prefix='/views')

    from .views.payrequest import pr_bp
    app.register_blueprint(pr_bp, url_prefix='/views')

    from .views.rental import re_bp
    app.register_blueprint(re_bp, url_prefix='/views')

    from .views.rent_object import ro_bp
    app.register_blueprint(ro_bp, url_prefix='/views')

    from .views.rent_external import rx_bp
    app.register_blueprint(rx_bp, url_prefix='/views')

    from .views.utilities import ut_bp
    app.register_blueprint(ut_bp, url_prefix='/views')

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