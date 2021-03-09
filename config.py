import os
basedir = os.path.abspath(os.path.dirname(__file__))

try:
    from myconfig import MyConfig
except:
    MyConfig = {}


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or MyConfig.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or getattr(MyConfig, 'MAIL_SERVER', None)
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or getattr(MyConfig, 'MAIL_PORT', None) or 25)
    MAIL_USE_TLS = (os.environ.get('MAIL_USE_TLS') or getattr(MyConfig, 'MAIL_USE_TLS', None)) is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or getattr(MyConfig, 'MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or getattr(MyConfig, 'MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or getattr(MyConfig, 'MAIL_DEFAULT_SENDER', None)
    MAIL_DEBUG = getattr(MyConfig, 'MAIL_DEBUG', False)
    MAIL_SUPPRESS_SEND = getattr(MyConfig, 'MAIL_SUPPRESS_SEND', False)
    ADMINS = getattr(MyConfig, 'ADMINS', None) or ['your-email@example.com']
    MYSQLDUMP_EXECUTABLE = getattr(MyConfig, 'MYSQLDUMP_EXECUTABLE', 'mysqldump')
    MYSQL_EXECUTABLE = getattr(MyConfig, 'MYSQL_EXECUTABLE', 'mysql')
