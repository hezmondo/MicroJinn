import sqlalchemy
from app import db
from app.dao.database import commit_to_database
from app.dao.money import get_money_items_loan
from app.models import Loan, LoanStat, LoanTran


def dbget_loan_row(loan_id):
    return Loan.query.get(loan_id)


def dbget_loans_all():
    return db.session.query(Loan).all()


def dbget_loans_nick():
    return db.session.query(Loan).filter(Loan.lender.ilike('%NJL%')).all()


def dbget_loanstat_data(loan_id):
    money_items = get_money_items_loan(loan_id)
    transactions = db.session.query(LoanTran).filter_by(loan_id=loan_id).all()
    stmt = " SELECT rate, start_date FROM loan_interest_rate WHERE loan_id = '{}' ".format(loan_id)
    rates = db.session.execute(stmt).fetchall()

    return money_items, rates, transactions


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
