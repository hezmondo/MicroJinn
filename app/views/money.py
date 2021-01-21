from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.money import get_moneyaccount, get_moneydets, get_moneydict, get_moneyitem, get_moneyitems, \
        post_moneyaccount, post_moneyitem

money_bp = Blueprint('money_bp', __name__)

@money_bp.route('/money', methods=['GET', 'POST'])
def money():
    accsums, moneydets = get_moneydets()

    return render_template('money.html', accsums=accsums, moneydets=moneydets)


@money_bp.route('/money_account/<int:id>', methods=['GET', 'POST'])
@login_required
def money_account(id):
    if request.method == "POST":
        acc_id = post_moneyaccount(id)

        return redirect('/money_account/{}'.format(acc_id))

    moneyacc = get_moneyaccount(id)

    return render_template('money_account.html', moneyacc=moneyacc)


@money_bp.route('/money_deduce/<int:id>', methods=['GET', 'POST'])
def money_deduce(id):
    action = request.args.get('action', "view", type=str)
    if action == "X":
        return redirect('/income_object/{}'.format(id))
    else:
        return redirect('/money_item/{}'.format(id))


@money_bp.route('/money_items/<int:id>', methods=["GET", "POST"])
@login_required
def money_items(id):
    # the incoming id is the account id
    money_dict = get_moneydict()
    accsums, moneyvals, transitems = get_moneyitems(id)

    return render_template('money_items.html', accsums=accsums, money_dict=money_dict, moneyvals=moneyvals,
                           transitems=transitems)


@money_bp.route('/money_item/<int:id>', methods=['GET', 'POST'])
def money_item(id):
    if request.method == "POST":
        bank_id = post_moneyitem(id)

        return redirect('/money_items/{}'.format(bank_id))

    money_dict = get_moneydict()
    money_item, cleared = get_moneyitem(id)

    return render_template('money_item.html', cleared=cleared, money_dict=money_dict, money_item=money_item)
