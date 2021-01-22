from flask import redirect, request, url_for
from app import db
from app.dao.functions import commit_to_database
from app.models import Agent, Charge, Digfile, Emailaccount, Form_letter, Incomealloc, Landlord, Loan, \
    Manager_external, Money_item, Pr_history, Property,  Rent, Rent_ex, Money_account


def delete_record(id):
    item = request.args.get('item')
    id_2 = request.args.get('id_2')
    id_dict = {}
    redir = ""
    if item == "agent":
        Agent.query.filter_by(id=id).delete()
        redir = "main_bp.agents"
    elif item == "bankitem":
        Money_item.query.filter_by(id=id).delete()
        redir = "views/money_items".format(id_2)
    elif item == "charge":
        Charge.query.filter_by(id=id).delete()
        # redir = "views/rent_"
        redir = "rent_bp.rent_"
    elif item == "dig":
        Digfile.query.filter_by(id=id).delete()
    elif item == "emailacc":
        Emailaccount.query.filter_by(id=id).delete()
        redir = "main_bp.email_accounts"
    elif item == "formletter":
        Form_letter.query.filter_by(id=id).delete()
        redir = "formletter_bp.form_, id={}".format(id_2)
    elif item == "incomealloc":
        Incomealloc.query.filter_by(id=id).delete()
    elif item == "landlord":
        Landlord.query.filter_by(id=id).delete()
        redir = "landlord_bp.landlords"
    elif item == "loan":
        Loan.query.filter_by(id=id).delete()
        # delete_loan_trans = Loan_trans.query.filter(Loan_trans.loan_id == id).all()
        # delete_loan_interest_rate = Loan_interest_rate.query.filter(Loan_interest_rate.loan_id == id).all()
        # db.session.delete(delete_loan_interest_rate)
        # db.session.delete(delete_loan_trans)
    elif item == "moneyacc":
        Money_account.query.filter_by(id=id).delete()
        redir = "money_bp.moneyaccs"
    elif item == "moneyitem":
        Money_item.query.filter_by(id=id).delete()
        redir = "money_bp.moneyitems"
    elif item == "property":
        Property.query.filter_by(id=id).delete()
        redir = "properties"
    elif item == "pr_file":
        Pr_history.query.filter_by(id=id).delete()
        redir = "pr_bp.pr_history"
        id_dict = {"rent_id": id_2}
    elif item == "rent":
        Rent.query.filter_by(id=id).delete()
        redir = "main_bp.home"
    else:
        redir = "main_bp.home"
    commit_to_database()

    return redir, id_2, id_dict


def get_emailaccounts():
    emailaccs = Emailaccount.query.all()

    return emailaccs


def get_emailaccount(id):
    emailacc = Emailaccount.query.filter(Emailaccount.id == id).one_or_none()

    return emailacc


def get_rent_ex(id):
    rent_ex = Rent_ex.query.join(Manager_external).with_entities(Rent_ex.rentcode,
                                                                 Rent_ex.propaddr, Rent_ex.tenantname, Rent_ex.owner, Rent_ex.rentpa,
                                                                 Rent_ex.arrears, Rent_ex.lastrentdate, Rent_ex.source, Rent_ex.status,
                                                                 Manager_external.codename, Manager_external.detail, Rent_ex.agentdetail) \
        .filter(Rent_ex.id == id).one_or_none()

    return rent_ex


def post_emailaccount(id):
    if id == 0:
        emailacc = Emailaccount()
    else:
        emailacc = Emailaccount.query.get(id)
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
    _id = emailacc.id
    db.session.commit()

    return _id
