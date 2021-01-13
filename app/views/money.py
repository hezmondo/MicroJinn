from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.money import get_moneyaccount, get_moneydets, get_moneydict, get_moneyitem, get_moneyitems, \
        post_moneyitem

mo_bp = Blueprint('mo_bp', __name__)

@mo_bp.route('/money', methods=['GET', 'POST'])
def money():
    accsums, moneydets = get_moneydets()

    return render_template('money.html', accsums=accsums, moneydets=moneydets)


@mo_bp.route('/money_account/<int:id>', methods=['GET', 'POST'])
@login_required
def money_account(id):
    moneyacc = get_moneyaccount(id)

    return render_template('money_account.html', moneyacc=moneyacc)


@mo_bp.route('/money_deduce/<int:id>', methods=['GET', 'POST'])
def money_deduce(id):
    action = request.args.get('action', "view", type=str)
    if action == "X":
        return redirect('/income_object/{}'.format(id))
    else:
        return redirect('/money_item/{}'.format(id))


@mo_bp.route('/money_items/<int:id>', methods=["GET", "POST"])
@login_required
def money_items(id):
    money_dict = get_moneydict()
    accsums, moneyvals, transitems = get_moneyitems(id)

    return render_template('money_items.html', accsums=accsums, money_dict=money_dict, moneyvals=moneyvals,
                           transitems=transitems)


@mo_bp.route('/money_item/<int:id>', methods=['GET', 'POST'])
def money_item(id):
    if request.method == "POST":
        bank_id = post_moneyitem(id)

        return redirect('/money_items/{}'.format(bank_id))

    money_dict = get_moneydict()
    money_item, cleared = get_moneyitem(id)

    return render_template('money_item.html', cleared=cleared, id=id, money_dict=money_dict, money_item=money_item)
