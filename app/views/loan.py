from flask import Blueprint, render_template, request
from flask_login import login_required
from app.main.loan import get_loan, get_loans, get_loan_stat, get_loan_statement
from app.modeltypes import AdvArr, Freqs

loan_bp = Blueprint('loan_bp', __name__)


@loan_bp.route('/loan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def loan(loan_id):
    loan = get_loan(loan_id)
    advarrdets = AdvArr.names()
    freqdets = Freqs.names()

    return render_template('loan.html', loan=loan, advarrdets=advarrdets, freqdets=freqdets)


@loan_bp.route('/loans', methods=['GET', 'POST'])
def loans():
    action = request.args.get('action', "view", type=str)
    loans, loansum = get_loans(action)

    return render_template('loans.html', loans=loans, loansum=loansum)


@loan_bp.route('/loanstat_dialog/<int:loan_id>', methods=["GET", "POST"])
def loanstat_dialog(loan_id):
    code = request.args.get('code', "ABC-123", type=str)

    return render_template('loanstat_dialog.html', code=code, loanid=loan_id)


@loan_bp.route('/loan_statement/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_statement(loan_id):
    # checksums, loancode, loanstatement = get_loan_statement(loan_id)
    checksums, loancode, loanstatement = get_loan_stat(loan_id)

    return render_template('loan_stat.html', checksums=checksums, loancode=loancode, loanstatement=loanstatement)
