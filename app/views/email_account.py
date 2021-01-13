from flask import Blueprint, render_template,  request
from flask_login import login_required
from app.dao.email import get_emailaccount, get_emailaccounts, post_emailaccount

em_bp = Blueprint('em_bp', __name__)

@em_bp.route('/email_accounts', methods=['GET'])
def email_accounts():
    emailaccs = get_emailaccounts()

    return render_template('email_accounts.html', emailaccs=emailaccs)

@em_bp.route('/email_account/<int:id>', methods=['GET', 'POST'])
@login_required
def email_account(id):
    if request.method == "POST":
        id = post_emailaccount(id)
    emailacc = get_emailaccount(id)

    return render_template('email_account.html', emailacc=emailacc)

