from flask import request
from app import db
from app.dao.functions import commit_to_database
from app.models import EmailAcc


def get_email_accs():
    emailaccs = EmailAcc.query.all()

    return emailaccs


def get_email_acc(email_acc_id):
    emailacc = EmailAcc.query.filter(EmailAcc.id == email_acc_id).one_or_none()

    return emailacc


def post_email_acc(email_acc_id):
    if email_acc_id == 0:
        emailacc = EmailAcc()
    else:
        emailacc = EmailAcc.query.get(email_acc_id)
    emailacc.smtp_server = request.form.get("smtp_server")
    emailacc.smtp_port = request.form.get("smtp_port")
    emailacc.smtp_timeout = request.form.get("smtp_timeout")
    emailacc.smtp_debug = request.form.get("smtp_debug")
    emailacc.smtp_tls = request.form.get("smtp_tls")
    emailacc.smtp_user = request.form.get("smtp_user")
    emailacc.smtp_password = request.form.get("smtp_password")
    emailacc.smtp_sendfrom = request.form.get("smtp_sendfrom")
    emailacc.imap_server = request.form.get("imap_server")
    emailacc.imap_port = request.form.get("imap_port")
    emailacc.imap_tls = request.form.get("imap_tls")
    emailacc.imap_user = request.form.get("imap_user")
    emailacc.imap_password = request.form.get("imap_password")
    emailacc.imap_sentfolder = request.form.get("imap_sentfolder")
    emailacc.imap_draftfolder = request.form.get("imap_draftfolder")
    db.session.add(emailacc)
    db.session.flush()
    email_acc_id = emailacc.id
    db.session.commit()
    return email_acc_id
