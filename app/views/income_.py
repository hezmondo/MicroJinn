from flask import Blueprint, render_template, redirect, request
from flask_login import login_required
from app.dao.income_ import get_income_dict, get_income_, get_incomes, post_income_

income_bp = Blueprint('income_bp', __name__)

@income_bp.route('/income/<int:id>', methods=['GET', 'POST'])
def income(id):
    # display recent income postings - id is money account id - if 0, display postings for all accounts
    incomes, incomevals = get_incomes(id)
    income_dict = get_income_dict("basic")

    return render_template('income.html', income_dict=income_dict, incomes=incomes, incomevals=incomevals)

@income_bp.route('/income_object/<int:id>', methods=['GET', 'POST'])
@login_required
def income_object(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_income_(id, action)

    income_dict = get_income_dict("enhanced")
    income, incomeallocs = get_income_(id)

    return render_template('income_.html', action=action, income=income, incomeallocs=incomeallocs,
                           income_dict=income_dict)
