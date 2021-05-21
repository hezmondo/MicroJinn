from threading import Thread
from flask import current_app
from flask_mail import Message
import socket
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    if recipients:
        # if any recipients are specified
        # then if there is a config variable 'MAIL_OVERRIDE_TO'
        # use that as the sole recipient
        # this allows you to relax while developing/testing,
        # sure in the knowledge that any emails sent will only be addressed to a set user, not the real recipient
        override_to = current_app.config.get('MAIL_OVERRIDE_TO', None)
        if override_to:
            recipients = [override_to]
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()


class SocketTimeout(object):
    """Handles timeout on global on `socket`."""

    def __init__(self, timeout=10.0):
        # left to its own devices, something as simple as a non-existent mail server host address
        # results in a "complete hang" for 4 and a half minutes...
        # the only way to influence this, because it is at the `socket` level
        # is to call socket.setdefaulttimeout()
        # see https://github.com/mattupstate/flask-mail/issues/114#issuecomment-272176255
        # we set it to 10 seconds by default here, should be enough
        self.originaldefaulttimeout = None
        self.timeout = timeout

    def __enter__(self):
        if self.timeout is not None:
            self.originaldefaulttimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.timeout)

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.timeout is not None:
            socket.setdefaulttimeout(self.originaldefaulttimeout)


def test_email_connect(appmail):
    response = ""
    with SocketTimeout():
        try:
            with appmail.connect() as _connection:
                if _connection.host:
                    if _connection.host.ehlo_resp:
                        response += str(_connection.host.ehlo_resp, 'utf-8', 'ignore')
                    if _connection.host.helo_resp:
                        response += str(_connection.host.helo_resp, 'utf-8', 'ignore')
        except Exception as ex:
            response += f"***Exception: {str(ex)}"

    return response


def test_send_email(appmail, recipient):
    sender = appmail.default_sender or appmail.username
    response = ""
    try:
        if not recipient:
            raise ValueError("No recipient specified to send email to")
        with SocketTimeout():
            send_email("Test email", sender, [recipient],
                       "This is a test email.",
                       "This is a <i>test email</i>.",
                       sync=True)
        response += f"The test email appears to have been sent successfully to '{recipient}'."
    except Exception as ex:
        response += f"***Exception: {str(ex)}"

    return response


def app_send_email(appmail, recipients, subject, html_body, attachments=None):
    # if recipients is a string, treat it as a ";"-separated list of recipients
    # this is (apparently) how multiple recipients are stored in records in the database
    # this method throws an exception if there is a problem sending the email
    if isinstance(recipients, str):
        recipients = recipients.split(";")
    sender = appmail.default_sender or appmail.username
    response = ""
    if not recipients:
        raise ValueError("No recipient specified to send email to")
    with SocketTimeout():
        send_email(subject, sender, recipients,
                   None,
                   html_body,
                   attachments,
                   sync=True)
    response += f"The test email appears to have been sent successfully to {''.join(recipients)}."

    return response


