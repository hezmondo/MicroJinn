import datetime
import sqlalchemy
from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.loan import get_loan, get_loans, get_loan_options, get_loanstatement

loan_bp = Blueprint('loan_bp', __name__)

@loan_bp.route('/loan/<int:id>', methods=['GET', 'POST'])
@login_required
def loan(id):
    loan = get_loan(id)
    advarrdets, freqdets = get_loan_options()

    return render_template('loan.html', loan=loan, advarrdets=advarrdets, freqdets=freqdets)


@loan_bp.route('/loans', methods=['GET', 'POST'])
def loans():
    action = request.args.get('action', "view", type=str)
    loans, loansum = get_loans(action)

    return render_template('loans.html', loans=loans, loansum=loansum)


@loan_bp.route('/loanstat_dialog/<int:id>', methods=["GET", "POST"])
def loanstat_dialog(id):
    return render_template('loanstat_dialog.html', loanid=id, today=datetime.date.today())


@loan_bp.route('/loan_statement/<int:id>', methods=["GET", "POST"])
@login_required
def loan_statement(id):
    if request.method == "POST":
        stat_date = request.form.get("statdate")
        rproxy = db.session.execute(sqlalchemy.text("CALL pop_loan_statement(:x, :y)"),
                                    params={"x": id, "y": stat_date})
        checksums = rproxy.fetchall()
        db.session.commit()
        loanstatement = get_loanstatement()
        loan = Loan.query.get(id)
        loancode = loan.code

        return render_template('loan_statement.html', loanstatement=loanstatement, loancode=loancode,
                               checksums=checksums)
