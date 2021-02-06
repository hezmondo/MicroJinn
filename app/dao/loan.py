import sqlalchemy
from app import db
from flask import request
from sqlalchemy import func
from app.models import Loan, LoanStat, TypeAdvArr, TypeFreq
from app.dao.functions import commit_to_database


def get_loan(loan_id):
    if request.method == "POST":
        loan_id = post_loan(loan_id)
    if loan_id != 0:
        loan = \
            Loan.query. \
                join(TypeAdvArr) \
                .join(TypeFreq) \
                .with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender, Loan.borrower,
                               Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa,
                               TypeAdvArr.advarrdet, TypeFreq.freqdet) \
                .filter(Loan.id == loan_id).one_or_none()
    else:
        loan = Loan()
        loan.id = 0
    return loan


def get_loan_options():
    # return options for each multiple choice control in loan page
    advarrdets = [value for (value,) in TypeAdvArr.query.with_entities(TypeAdvArr.advarrdet).all()]
    freqdets = [value for (value,) in TypeFreq.query.with_entities(TypeFreq.freqdet).all()]

    return advarrdets, freqdets


def get_loans(action):
    if action == "Nick":
        loans = Loan.query.with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender,
                                         Loan.borrower,
                                         Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa) \
            .filter(Loan.lender.ilike('%NJL%')).all()
        loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('tot_val'),
                                           func.sum(Loan.interestpa).label('totint')) \
            .filter(Loan.lender.ilike('%NJL%')).first()
    else:
        loans = Loan.query.with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender,
                                         Loan.borrower,
                                         Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa).all()
        loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('tot_val'),
                                           func.sum(Loan.interestpa).label('totint')).filter().first()

    return loans, loansum


def post_loan(loan_id):
    loan = Loan.query.get(loan_id) or Loan()
    loan.code = request.form.get("loancode")
    loan.interest_rate = request.form.get("interest_rate")
    loan.end_date = request.form.get("end_date")
    frequency = request.form.get("frequency")
    loan.frequency = \
        TypeFreq.query.with_entities(TypeFreq.id).filter(TypeFreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    loan.advarr_id = \
        TypeAdvArr.query.with_entities(TypeAdvArr.id).filter(TypeAdvArr.advarrdet == advarr).one()[0]
    loan.lender = request.form.get("lender")
    loan.borrower = request.form.get("borrower")
    loan.notes = request.form.get("notes")
    # loan.val_date = request.form.get("val_date")
    # loan.valuation = request.form.get("valuation")
    # delete_loan_trans = LoanTran.query.filter(LoanTran.loan_id == id).all()
    # delete_loan_interest_rate = LoanIntRate.query.filter(LoanIntRate.loan_id == id).all()
    # db.session.delete(delete_loan_interest_rate)
    # db.session.delete(delete_loan_trans)

    db.session.add(loan)
    db.session.flush()
    loan_id = loan.id
    commit_to_database()

    return loan_id


def get_loan_statement(loan_id):
    stat_date = request.form.get("statdate")
    rproxy = db.session.execute(sqlalchemy.text("CALL pop_loan_statement(:x, :y)"),
                                params={"x": loan_id, "y": stat_date})
    checksums = rproxy.fetchall()
    db.session.commit()
    loanstatement = LoanStat.query.with_entities(LoanStat.id, LoanStat.date, LoanStat.memo,
                                                 LoanStat.transaction, LoanStat.rate,
                                                 LoanStat.interest,
                                                 LoanStat.add_interest, LoanStat.balance).all()
    loan = Loan.query.get(loan_id)
    loancode = loan.code

    return checksums, loancode, loanstatement