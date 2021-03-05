class MyConfig(object):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://<username>:<password>>@localhost/mjinn'
    # uncomment and set all MAIL_ variables to enable emailing
    # first set is for "emulated" mailing on development machine
    # to use, in another window/Command Prompt run:
    # python3 -m smtpd -n -c DebuggingServer localhost:8025
    # MAIL_SERVER = 'localhost'
    # MAIL_PORT = 8025
    # MAIL_USE_TLS = None
    # MAIL_USERNAME = None
    # MAIL_PASSWORD = None
    # second set is to use gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = '<username>@gmail.com'
    MAIL_PASSWORD = '<password>'
    # MAIL_DEFAULT_SENDER = '<username>@gmail.com'
    # MAIL_DEBUG = True
    ADMINS = ['<some-user>@gmail.com']
    # uncomment MYSQLDUMP_EXECUTABLE and set to command/path if not default 'mysqldump'
    # MYSQLDUMP_EXECUTABLE = 'mysqldump'
    # uncomment MYSQL_EXECUTABLE and set to command/path if not default 'mysql'
    # MYSQL_EXECUTABLE = 'mysql'
