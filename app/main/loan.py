from app import db
from flask import request
from sqlalchemy import desc, func
from app.models import Loan, Loan_statement, Typeadvarr, Typefreq

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
