from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from app.dao.money import delete_money_item, get_moneyaccount, get_moneydets, get_moneydict, get_money_item, \
        get_money_items, post_moneyaccount, post_money_item

money_bp = Blueprint('money_bp', __name__)

@money_bp.route('/money', methods=['GET', 'POST'])
def money():
    accsums, moneydets = get_moneydets()
    return render_template('money.html', accsums=accsums, moneydets=moneydets)


@money_bp.route('/money_account/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def money_account(acc_id):
    if request.method == "POST":
        acc_id = post_moneyaccount(acc_id)
        return redirect('/money_account/{}'.format(acc_id))
    moneyacc = get_moneyaccount(acc_id)
    return render_template('money_account.html', moneyacc=moneyacc)


@money_bp.route('/money_deduce/<int:item_id>/<mode>', methods=['GET', 'POST'])
def money_deduce(item_id, mode='Y'):    #determines if table item is income or money - clunky and horrible
    # mode = request.args.get('mode', "X", type=str)
    if mode == "X":
        return redirect(url_for('income_bp.income_item', income_id=item_id))
    else:
        return redirect(url_for('money_bp.money_item', money_item_id=item_id))


@money_bp.route('/money_item/<int:money_item_id>', methods=['GET', 'POST'])
def money_item(money_item_id, acc_desc="all accounts"):
    if request.method == "POST":
        id_ = post_money_item(money_item_id)
        return redirect(url_for('money_bp.money_item', id=id_))
    money_dict = get_moneydict()
    money_item, cleared = get_money_item(money_item_id, acc_desc)
    return render_template('money_item.html', cleared=cleared, money_dict=money_dict, money_item=money_item)


@money_bp.route('/money_item_delete/<int:money_item_id>/<int:acc_id>')
@login_required
def money_item_delete(money_item_id, acc_id):
    delete_money_item(money_item_id)
    return redirect(url_for('money_bp.money_items', acc_id=acc_id))


@money_bp.route('/money_items/<int:acc_id>', methods=["GET", "POST"])
@login_required
def money_items(acc_id):  # if account id is 0 show items for all accounts
    # post values are filter values, so dealt with in the following get function
    accsums, moneyvals, transitems = get_money_items(acc_id)
    money_dict = get_moneydict("plus_all")
    return render_template('money_items.html', accsums=accsums, money_dict=money_dict, moneyvals=moneyvals,
                           transitems=transitems)
