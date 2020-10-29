from flask import flash, redirect, request
from app import db
from app.main.functions import commit_to_database
from app.models import Agent, Formletter, Headrent, Loan, Money_category, Money_item, \
    Rental, Template, Typeadvarr, Money_account, Typefreq, Typedoc, Emailaccount


def post_formletter(id, action):
    if action == "edit":
        formletter = Formletter.query.get(id)
    else:
        formletter = Formletter()
    formletter.code = request.form.get("code")
    formletter.summary = request.form.get("summary")
    formletter.subject = request.form.get("subject")
    formletter.block = request.form.get("block")
    formletter.bold = request.form.get("bold")
    doctype = request.form.get("doc_type")
    formletter.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter \
            (Typedoc.desc == doctype).one()[0]
    template = request.form.get("template")
    formletter.template_id = \
        Template.query.with_entities(Template.id).filter \
            (Template.code == template).one()[0]
    db.session.add(formletter)
    db.session.commit()
    id_ = formletter.id

    return id_


def post_emailaccount(id, action):
    if action == "edit":
        emailacc = Emailaccount.query.get(id)
    else:
        emailacc = Emailaccount()
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
    db.session.commit()
    id_ = emailacc.id

    return id_


def post_headrent(id, action):
    if action == "edit":
        headrent = Headrent.query.get(id)
    else:
        headrent = Agent()
    headrent.agdetails = request.form.get("agdetails")
    db.session.add(headrent)
    commit_to_database()
    id_ = headrent.id

    return id_


def post_loan(id, action):
    if action == "edit":
        loan = Loan.query.get(id)
    else:
        loan = Loan()
    loan.code = request.form.get("loancode")
    loan.interest_rate = request.form.get("interest_rate")
    loan.end_date = request.form.get("end_date")
    frequency = request.form.get("frequency")
    loan.frequency = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    loan.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    loan.lender = request.form.get("lender")
    loan.borrower = request.form.get("borrower")
    loan.notes = request.form.get("notes")
    # loan.val_date = request.form.get("val_date")
    # loan.valuation = request.form.get("valuation")
    db.session.add(loan)
    db.session.commit()
    id_ = loan.id

    return id_


def post_moneyaccount(id, action):
    if action == "edit":
        moneyacc = Money_account.query.get(id)
    else:
        moneyacc = Money_account()
    moneyacc.bankname = request.form.get("bankname")
    moneyacc.accname = request.form.get("accname")
    moneyacc.sortcode = request.form.get("sortcode")
    moneyacc.accnum = request.form.get("accnum")
    moneyacc.accdesc = request.form.get("accdesc")
    db.session.add(moneyacc)
    db.session.commit()
    id_ = moneyacc.id

    return id_


def post_moneyitem(id, action):
    if action == "edit":
        bankitem = Money_item.query.get(id)
    else:
        bankitem = Money_item()
    bankitem.num = request.form.get("num")
    bankitem.date = request.form.get("date")
    bankitem.amount = request.form.get("amount")
    bankitem.payer = request.form.get("payer")
    accdesc = request.form.get("accdesc")
    bankitem.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == accdesc).one()[0]
    cleared = request.form.get("cleared")
    bankitem.cleared = 1 if cleared == "cleared" else 0
    cat = request.form.get("category")
    bankitem.cat_name = \
        Money_category.query.with_entities(Money_category.id).filter \
            (Money_category.cat_name == cat).one()[0]
    db.session.add(bankitem)
    db.session.commit()
    id_ = bankitem.id

    return id_


def post_rental(id, action):
    if action == "edit":
        rental = Rental.query.get(id)
    else:
        rental = Rental()
    rental.propaddr = request.form.get("propaddr")
    rental.tenantname = request.form.get("tenantname")
    rental.rentpa = request.form.get("rentpa")
    rental.arrears = request.form.get("arrears")
    rental.startrentdate = request.form.get("startrentdate")
    if rental.astdate:
        rental.astdate = request.form.get("astdate")
    rental.lastgastest = request.form.get("lastgastest")
    rental.note = request.form.get("note")
    frequency = request.form.get("frequency")
    rental.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    rental.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    db.session.add(rental)
    db.session.commit()
    id_ = rental.id

    return id_
