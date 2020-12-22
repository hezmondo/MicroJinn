from app import db
from datetime import date
from flask import flash, redirect, url_for, request, session
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app.main.functions import commit_to_database
from app.models import Agent, Form_letter, Pr_form, Headrent, Income, Incomealloc, Landlord, \
    Loan, Loan_statement, Manager, Rent, Rental, Rental_statement, \
    Typeadvarr, Money_account, Template, Typefreq, Typedoc, Typepayment, Typestatus, Typetenure, Emailaccount


# email accounts
def get_emailaccounts():
    emailaccs = Emailaccount.query.all()

    return emailaccs


def get_emailaccount(id):
    emailacc = Emailaccount.query.filter(Emailaccount.id == id).one_or_none()

    return emailacc


# formletters
def get_formletter(id):
    formletter = Form_letter.query.join(Typedoc).join(Template).with_entities(Form_letter.id, Form_letter.code,
                                                                              Form_letter.description,
                                                                              Form_letter.subject, Form_letter.block,
                                                                              Typedoc.desc,
                                                                              Template.desc.label("template")) \
        .filter(Form_letter.id == id).one_or_none()

    return formletter


def get_formletters(action):
    if request.method == "POST":
        code = request.form.get("code") or ""
        summary = request.form.get("summary") or ""
        subject = request.form.get("subject") or ""
        part1 = request.form.get("part1") or ""
        block = request.form.get("block") or ""
        formletters = Form_letter.query.filter(Form_letter.code.ilike('%{}%'.format(code)),
                                               Form_letter.subject.ilike('%{}%'.format(summary)),
                                               Form_letter.subject.ilike('%{}%'.format(subject)),
                                               Form_letter.part1.ilike('%{}%'.format(part1)),
                                               Form_letter.block.ilike('%{}%'.format(block))).all()
    elif action == "lease":
        formletters = Form_letter.query.filter(Form_letter.code.ilike('LEQ-%'))
    else:
        formletters = Form_letter.query.all()

    return formletters


def get_pr_form(id):
    formpayrequest = Pr_form.query.filter(Pr_form.id == id).one_or_none()
    return formpayrequest


def get_pr_forms():
    return Pr_form.query.all()


# head rents
def get_headrents():
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    statusdets.insert(0, "all statuses")
    headrents = Headrent.query.join(Typestatus).outerjoin(Agent).with_entities(Agent.agdetails, Headrent.id,
                                                                               Headrent.hrcode, Headrent.rentpa,
                                                                               Headrent.arrears, Headrent.freq_id,
                                                                               Headrent.lastrentdate,
                                                                               Headrent.propaddr,
                                                                               func.samjinn.next_date(
                                                                                   Headrent.lastrentdate,
                                                                                   Headrent.freq_id, 1).label(
                                                                                   'nextrentdate'),
                                                                               Typestatus.statusdet).limit(100).all()
    return headrents, statusdets


def get_headrent(id):
    headrent = \
        Headrent.query \
            .join(Landlord) \
            .outerjoin(Agent) \
            .join(Typeadvarr) \
            .join(Typefreq) \
            .join(Typestatus) \
            .join(Typetenure) \
            .with_entities(Headrent.id, Headrent.hrcode, Headrent.arrears, Headrent.datecode, Headrent.lastrentdate,
                           Headrent.propaddr, Headrent.rentpa, Headrent.reference, Headrent.note, Headrent.source,
                           Landlord.landlordname, Agent.agdetails, Typeadvarr.advarrdet, Typefreq.freqdet,
                           Typestatus.statusdet, Typetenure.tenuredet,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.samjinn.next_rent_date(Headrent.id, 2, 1).label('nextrentdate')) \
            .filter(Headrent.id == id) \
            .one_or_none()

    return headrent


# loans
def get_loan(id):
    loan = \
        Loan.query.join(Typeadvarr).join(Typefreq).with_entities(Loan.id, Loan.code, Loan.interest_rate,
                                                                 Loan.end_date, Loan.lender, Loan.borrower, Loan.notes,
                                                                 Loan.val_date, Loan.valuation,
                                                                 Loan.interestpa, Typeadvarr.advarrdet,
                                                                 Typefreq.freqdet) \
            .filter(Loan.id == id).one_or_none()

    return loan


def get_loan_options():
    # return options for each multiple choice control in loan page
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]

    return advarrdets, freqdets


def get_loans(action):
    if action == "Nick":
        loans = Loan.query.with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender,
                                         Loan.borrower,
                                         Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa) \
            .filter(Loan.lender.ilike('%NJL%')).all()
        loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('totval'),
                                           func.sum(Loan.interestpa).label('totint')) \
            .filter(Loan.lender.ilike('%NJL%')).first()
    else:
        loans = Loan.query.with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender,
                                         Loan.borrower,
                                         Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa).all()
        loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('totval'),
                                           func.sum(Loan.interestpa).label('totint')).filter().first()

    return loans, loansum


def get_loanstatement():
    loanstatement = Loan_statement.query.with_entities(Loan_statement.id, Loan_statement.date, Loan_statement.memo,
                                                       Loan_statement.transaction, Loan_statement.rate,
                                                       Loan_statement.interest,
                                                       Loan_statement.add_interest, Loan_statement.balance).all()

    return loanstatement


# mail
def getmaildata(rent_id, income_id=0):
    if income_id == 0:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                                                                                    Income.date.label("paydate"),
                                                                                    Income.amount.label("payamount"),
                                                                                    Typepayment.paytypedet) \
            .filter(Incomealloc.rent_id == rent_id).order_by(desc(Income.date)).limit(1).one_or_none()
        # income_id = incomedata.id
    else:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                                                                                    Income.date.label("paydate"),
                                                                                    Income.amount.label("payamount"),
                                                                                    Typepayment.paytypedet) \
            .filter(Income.id == income_id).first()
    # allocdata = Incomealloc.join(Chargetype).with_entities(Incomealloc.id, Incomealloc.income_id,
    #                     Incomealloc.rentcode, Incomealloc.amount.label("alloctot"),
    #                     Chargetype.chargedesc).filter(Incomealloc.income_id == income_id).all()
    allocdata = None
    bankdata = Money_account.query.join(Landlord).join(Rent).with_entities(Money_account.accname, Money_account.accnum,
                                                                           Money_account.sortcode,
                                                                           Money_account.bankname).filter(
        Rent.id == rent_id) \
        .one_or_none()
    addressdata = Landlord.query.join(Rent).join(Manager).with_entities(
        Landlord.landlordaddr, Manager.manageraddr, Manager.manageraddr2,
    ).filter(Rent.id == rent_id).one_or_none()

    return incomedata, allocdata, bankdata, addressdata


# rentals
def get_rental(id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    rental = Rental.query.join(Typeadvarr).join(Typefreq).with_entities(Rental.id, Rental.rentalcode, Rental.arrears,
                                                                        Rental.startrentdate, Rental.astdate,
                                                                        Rental.lastgastest, Rental.note,
                                                                        Rental.propaddr, Rental.rentpa,
                                                                        Rental.tenantname, Typeadvarr.advarrdet,
                                                                        Typefreq.freqdet).filter(
        Rental.id == id).one_or_none()
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    return rental, advarrdets, freqdets


def getrentals():
    rentals = Rental.query.all()
    rentsum = Rental.query.with_entities(func.sum(Rental.rentpa).label('totrent')).filter().first()[0]

    return rentals, rentsum


def get_rentalstatement():
    rentalstatem = Rental_statement.query.all()

    return rentalstatem


def post_formletter(id, action):
    if action == "edit":
        formletter = Form_letter.query.get(id)
    else:
        formletter = Form_letter()
    formletter.code = request.form.get("code")
    formletter.description = request.form.get("description")
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
