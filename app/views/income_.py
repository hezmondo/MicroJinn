from flask import Blueprint, render_template, redirect, request
from flask_login import login_required
from app.dao.income_ import get_income_dict, get_income_, get_incomes, post_income_

income_bp = Blueprint('income_bp', __name__)

@income_bp.route('/income/<int:acc_id>', methods=['GET', 'POST'])
def income(acc_id):
    # display recent income postings for money account id or (if 0) for all accounts
    # if rent_id is passed it will be interpreted in the following get
    incomes, incomevals = get_incomes(acc_id)
    income_dict = get_income_dict("basic")

    return render_template('income.html', income_dict=income_dict, incomes=incomes, incomevals=incomevals)

@income_bp.route('/income_item/<int:income_id>', methods=['GET', 'POST'])
@login_required
def income_item(income_id):
    # action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        income_id = post_income_(income_id)

    income_dict = get_income_dict("enhanced")
    income, incomeallocs = get_income_(income_id)

    return render_template('income_item.html', income=income, incomeallocs=incomeallocs,
                           income_dict=income_dict)
