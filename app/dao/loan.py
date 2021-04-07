import sqlalchemy
from sqlalchemy import asc, select, text
from sqlalchemy.orm import joinedload, load_only
from app import db
from app.dao.database import commit_to_database
from app.models import Loan, LoanIntRate, LoanStat, LoanTran, MoneyItem


def dbget_loan_row(loan_id):
    return Loan.query.get(loan_id)


def dbget_loans_all():
    return db.session.query(Loan).all()


def dbget_loans_nick():
    return db.session.query(Loan).filter(Loan.lender.ilike('%NJL%')).all()


def dbget_loanstat_data(loan_id):
    transactions = db.session.query(MoneyItem). \
        filter(MoneyItem.cat_id==42, MoneyItem.num==loan_id) \
        .options(load_only('id', 'date', 'memo', 'amount')) \
        .union_all(db.session.query(LoanTran) \
        .options(load_only('id', 'date', 'memo', 'amount')) \
        .filter(LoanTran.loan_id==loan_id)) \
        .order_by(MoneyItem.date, LoanTran.date)
    stmt = " SELECT rate, start_date FROM loan_interest_rate WHERE loan_id = '{}' ".format(loan_id)
    rates = db.session.execute(stmt).fetchall()

    return rates, transactions


def post_loan(loan):
    db.session.add(loan)
    db.session.flush()
    loan_id = loan.id
    commit_to_database()

    return loan_id


def dbget_loan_statement(loan_id, stat_date):
    rproxy = db.session.execute(sqlalchemy.text("CALL pop_loan_statement(:x, :y)"),
                                params={"x": loan_id, "y": stat_date})
    checksums = rproxy.fetchall()
    commit_to_database()
    loanstatement = LoanStat.query.with_entities(LoanStat.id, LoanStat.date, LoanStat.memo,
                                                 LoanStat.transaction, LoanStat.rate,
                                                 LoanStat.interest,
                                                 LoanStat.add_interest, LoanStat.balance).all()

    return checksums, loanstatement
