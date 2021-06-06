from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from app.dao.money import get_money_acc, get_moneydets, get_moneydict, \
    get_money_item, get_money_items, post_money_acc, post_money_acc_new, post_money_item
from app import db

money_bp = Blueprint('money_bp', __name__)


@money_bp.route('/money', methods=['GET', 'POST'])
def money():
    message = request.args.get('message')
    accsums, moneydets = get_moneydets()

    return render_template('money.html', accsums=accsums, moneydets=moneydets, message=message)


@money_bp.route('/money_acc/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def money_acc(acc_id):
    message = request.args.get('message')
    if request.method == "POST":
        try:
            acc_id = post_money_acc(acc_id)
        except Exception as ex:
            message = f"Error posting new money account. Database rolled back. Error: {str(ex)}"
            db.sesssion.rollback()
        return redirect(url_for('money_bp.money_acc', acc_id=acc_id, message=message))
    moneyacc = get_money_acc(acc_id)

    return render_template('money_acc.html', moneyacc=moneyacc, message=message)


@money_bp.route('/money_acc_new', methods=['GET', 'POST'])
@login_required
def money_acc_new():
    if request.method == "POST":
        try:
            acc_id = post_money_acc_new()
            message = 'New account created successfully.'
            return redirect(url_for('money_bp.money', acc_id=acc_id, message=message))
        except Exception as ex:
            message = f"Error posting new money account. Database rolled back. Error: {str(ex)}"
            db.sesssion.rollback()
            return redirect(url_for('money_bp.money', message=message))
    return render_template('money_acc.html')


@money_bp.route('/money_deduce/<int:item_id>/<mode>', methods=['GET', 'POST'])
def money_deduce(item_id, mode='Y'):    #determines if table item is income or money - clunky and horrible
    # mode = request.args.get('mode', "X", type=str)
    if mode == "X":
        return redirect(url_for('income_bp.income_item', income_id=item_id))
    else:
        return redirect(url_for('money_bp.money_item', money_item_id=item_id))


@money_bp.route('/money_item/<int:money_item_id>', methods=['GET', 'POST'])
def money_item(money_item_id):
    if request.method == "POST":
        money_item_id = post_money_item(money_item_id)
        return redirect(url_for('money_bp.money_item', money_item_id=money_item_id))
    money_dict = get_moneydict()
    money_item, cleared = get_money_item(money_item_id)

    return render_template('money_item.html', cleared=cleared, money_dict=money_dict, money_item=money_item)


@money_bp.route('/money_items/<int:acc_id>', methods=["GET", "POST"])
@login_required
def money_items(acc_id):  # if account id is 0 show items for all accounts
    # post values are filter values, so dealt with in the following get function
    accsums, moneyvals, transitems = get_money_items(acc_id)
    money_dict = get_moneydict("plus_all")

    return render_template('money_items.html', accsums=accsums, money_dict=money_dict, moneyvals=moneyvals,
                           transitems=transitems)
