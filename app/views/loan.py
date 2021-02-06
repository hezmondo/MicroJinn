import datetime
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.dao.loan import get_loan, get_loans, get_loan_options, get_loan_statement

loan_bp = Blueprint('loan_bp', __name__)


@loan_bp.route('/loan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def loan(loan_id):
    loan = get_loan(loan_id)
    advarrdets, freqdets = get_loan_options()

    return render_template('loan.html', loan=loan, advarrdets=advarrdets, freqdets=freqdets)


@loan_bp.route('/loans', methods=['GET', 'POST'])
def loans():
    action = request.args.get('action', "view", type=str)
    loans, loansum = get_loans(action)

    return render_template('loans.html', loans=loans, loansum=loansum)


@loan_bp.route('/loanstat_dialog/<int:loan_id>', methods=["GET", "POST"])
def loanstat_dialog(loan_id):
    return render_template('loanstat_dialog.html', loanid=loan_id, today=datetime.date.today())


@loan_bp.route('/loan_statement/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_statement(loan_id):
    checksums, loancode, loanstatement = get_loan_statement(loan_id)
    return render_template('loan_statement.html', checksums=checksums, loancode=loancode, loanstatement=loanstatement)
