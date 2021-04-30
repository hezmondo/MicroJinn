from datetime import date, datetime
from decimal import Decimal
from flask import request
from app.dao.loan import dbget_loan_statement, dbget_loan_row, dbget_loans_all, dbget_loanstat_data, \
    dbget_loans_nick, post_loan
from app.main.common import inc_date
from app.main.functions import money
from app.models import Loan
from app.modeltypes import AdvArr, Freqs


def get_loan(loan_id):
    if request.method == "POST":
        loan_id = update_loan(loan_id)
    if loan_id == 0:
        loan = {}
    else:
        loan = dbget_loan_row(loan_id)
        loan.freqdet = Freqs.get_name(loan.freq_id)

    return loan


def get_loans(action):
    if action == "Nick":
        loans =  dbget_loans_nick()
    else:
        loans = dbget_loans_all()

    loansum ={}
    loansum['totval'] = Decimal(0)
    loansum['totint'] = Decimal(0)
    for loan in loans:
        loansum['totval'] += loan.valuation
        loansum['totint'] += loan.interestpa

    return loans, loansum


def update_loan(loan_id):
    loan = Loan() if loan_id == 0 else dbget_loan_row(loan_id)
    loan.code = request.form.get("loancode")
    loan.interest_rate = request.form.get("interest_rate")
    loan.end_date = request.form.get("end_date")
    loan.freq_id = Freqs.get_id(request.form.get("frequency"))
    loan.advarr_id = AdvArr.get_id(request.form.get("advarr"))
    loan.lender = request.form.get("lender")
    loan.borrower = request.form.get("borrower")
    loan.notes = request.form.get("notes")
    # loan.val_date = request.form.get("val_date")
    # loan.valuation = request.form.get("valuation")
    # delete_loan_trans = LoanTran.query.filter(LoanTran.loan_id == id).all()
    # delete_loan_interest_rate = LoanIntRate.query.filter(LoanIntRate.loan_id == id).all()
    # db.session.delete(delete_loan_interest_rate)
    # db.session.delete(delete_loan_trans)
    loan_id = post_loan(loan)

    return loan_id


def get_loan_statement(loan_id):
    stat_date = request.form.get("statdate")
    loancode = request.form.get("loancode")
    checksums, loanstatement = dbget_loan_statement(loan_id, stat_date)

    return checksums, loancode, loanstatement

def get_loan_stat(loan_id):
    stat_date = datetime.strptime(request.form.get("statdate"), '%Y-%m-%d')
    stat_date = stat_date.date()
    loancode = request.form.get("loancode")
    loan = dbget_loan_row(loan_id)
    money_items, rates, transactions = dbget_loanstat_data(loan_id)
    checksums = {'id': 1, 'memo': 'abc', 'advanced': 0, 'interest': 0, 'repaid': 0}
    loanstatement = []
    for item in money_items:
        item_row = {'id': item.id, 'date': item.date, 'memo': item.memo, 'amount': -item.amount, 'rate': 0, 'interest': 0, 'addinterest': 'no', 'balance': 0}
        loanstatement.append(item_row)
    for item in transactions:
        item_row = {'id': item.id, 'date': item.date, 'memo': item.memo, 'amount': item.amount, 'rate': 0, 'interest': 0, 'addinterest': 'no', 'balance': 0}
        loanstatement.append(item_row)
    min_date = min(item['date'] for item in loanstatement)
    int_date = inc_date(min_date, loan.freq_id, 1)
    freqdet = Freqs.get_name(loan.freq_id)
    while int_date <= date.today():
        item_row = {'id': 0, 'date': int_date, 'memo': f"interest added {freqdet}", 'amount': 0, 'rate': 0, 'interest': 0, 'addinterest': 'yes', 'balance': 0}
        loanstatement.append(item_row)
        int_date = inc_date(int_date, loan.freq_id, 1)
    loanstatement = sorted(loanstatement, key=lambda k: k['date'])
    rate1 = rates[0][0]
    date1 = rates[0][1]
    bal = money(loanstatement[0]['amount'])
    interest_pending = money(0)
    num = len(loanstatement)
    for i in range(1, num):
        loanstatement[i]['rate'] = rate1
        daysno = (loanstatement[i]['date'] - date1).days
        daysno = Decimal(daysno)
        interest = money(rate1 * bal * daysno / Decimal(36525)) if daysno > 0 else money(0)
        loanstatement[i]['interest'] = interest
        date1 = loanstatement[i]['date']
        interest_pending = money(interest_pending + interest)
        loanstatement[i]['balance'] = money(bal + loanstatement[i]['amount'])
        if loanstatement[i]['addinterest'] == 'yes':
            loanstatement[i]['balance'] = money(loanstatement[i]['balance'] + interest_pending)
            interest_pending = money(0)
        bal = money(loanstatement[i]['balance'])

    return checksums, loancode, loanstatement
