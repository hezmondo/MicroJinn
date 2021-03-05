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


def test_email_connect(appmail):
    response = ""
    originaldefaulttimeout = socket.getdefaulttimeout()
    try:
        # left to its own devices, something as simple as a non-existent mail server host address
        # results in a "complete hang" for 4 and a half minutes...
        # the only way to influence this, because it is at the `socket` level
        # is to call socket.setdefaulttimeout()
        # see https://github.com/mattupstate/flask-mail/issues/114#issuecomment-272176255
        # we set it to 10 seconds here, should be enough
        socket.setdefaulttimeout(10.0)
        with appmail.connect() as _connection:
            if _connection.host:
                if _connection.host.ehlo_resp:
                    response += str(_connection.host.ehlo_resp, 'utf-8', 'ignore')
                if _connection.host.helo_resp:
                    response += str(_connection.host.helo_resp, 'utf-8', 'ignore')
    except Exception as ex:
        response += f"***Exception: {str(ex)}"
    finally:
        socket.setdefaulttimeout(originaldefaulttimeout)

    return response


def test_send_email(appmail, recipient):
    sender = appmail.default_sender or appmail.username
    response = ""
    originaldefaulttimeout = socket.getdefaulttimeout()
    try:
        if not recipient:
            raise ValueError("No recipient specified to send email to")
        # left to its own devices, something as simple as a non-existent mail server host address
        # results in a "complete hang" for 4 and a half minutes...
        # the only way to influence this, because it is at the `socket` level
        # is to call socket.setdefaulttimeout()
        # see https://github.com/mattupstate/flask-mail/issues/114#issuecomment-272176255
        # we set it to 10 seconds here, should be enough
        socket.setdefaulttimeout(10.0)
        send_email("Test email", sender, [recipient],
                   "This is a test email.",
                   "This is a <i>test email</i>.",
                   sync=True)
        response += f"The test email appears to have been sent successfully to '{recipient}'."
    except Exception as ex:
        response += f"***Exception: {str(ex)}"
    finally:
        socket.setdefaulttimeout(originaldefaulttimeout)

    return response


