import datetime
from datetime import date
from flask import request
from sqlalchemy import desc, func, literal
from app import db
from app.models import Income, Incomealloc, Money_account, Money_category, Money_item


def get_moneyaccount(id):
    # get values for a single account and deal with post
    if id == 0:
        moneyacc = Money_account()
        moneyacc.id = 0
    else:
        moneyacc = Money_account.query.filter(Money_account.id == id).one_or_none()

    return moneyacc


def get_moneydets():
    moneydets = Money_account.query.with_entities(Money_account.id, Money_account.bankname, Money_account.accname,
                  Money_account.sortcode, Money_account.accnum, Money_account.accdesc,
                           func.samjinn.acc_balance(Money_account.id, 1, date.today()).label('cbalance'),
                           func.samjinn.acc_balance(Money_account.id, 0, date.today()).label('ubalance')).all()

    accsums = Money_account.query.with_entities(func.samjinn.acc_total(1).label('cleared'),
                                            func.samjinn.acc_total(0).label('uncleared')).filter().first()

    return accsums, moneydets


def get_moneydict():
    # return options for multiple choice controls in money_item and money_items pages
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs_all = bankaccs
    bankaccs_all.insert(0, "all accounts")
    cats = [value for (value,) in Money_category.query.with_entities(Money_category.cat_name).all()]
    cats_all = cats
    cats_all.insert(0, "all categories")
    cleareds = ["cleared", "uncleared"]
    cleareds_all = cleareds
    cleareds_all.insert(0, "all cleareds")
    money_dict = {
        "bankaccs": bankaccs,
        "bankaccs_all": bankaccs_all,
        "cats": cats,
        "cats_all": cats_all,
        "cleareds": cleareds,
        "cleareds_all": cleareds_all
    }

    return money_dict


def get_moneyitem(id):
    if id == 0:
        moneyitem = Money_item()
        moneyitem.id = 0
        moneyitem.date = datetime.date.today()
        cleared = "cleared"
    else:
        moneyitem = Money_item.query.join(Money_account).join(Money_category).with_entities(Money_item.id,
                    Money_item.num, Money_item.date, Money_item.payer, Money_item.amount, Money_item.memo,
                    Money_account.id.label("acc_id"), Money_account.accdesc, Money_category.cat_name,
                    Money_item.cleared).filter(Money_item.id == id).one_or_none()

        cleared = "cleared" if moneyitem.cleared == 1 else "uncleared"

    return moneyitem, cleared


def get_moneyitems(id):
    money_filter = []
    income_filter = [Income.paytype_id != 1]
    moneyvals= {
        'accdesc': 'all accounts',
        'payee': 'all payees',
        'memo': 'all memos',
        'category': 'all categories',
        'cleared': 'all cleareds',
        'accsums': 0.00
    }
    if id != 0:
        money_filter.append(Money_account.id == id)
        income_filter.append(Money_account.id == id)
        bankacc = Money_account.query.filter(Money_account.id == id).one_or_none()
        moneyvals['bankacc'] = bankacc.accdesc
    if request.method == "POST":
        payee = request.form.get("payee") or "all"
        if payee != "all":
            money_filter.append(Money_item.payer.ilike('%{}%'.format(payee)))
            income_filter.append(Income.payer.ilike('%{}%'.format(payee)))
            moneyvals['payee'] = payee
        memo = request.form.get("memo") or "all"
        if memo != "all":
            money_filter.append(Money_item.memo.ilike('%{}%'.format(memo)))
            income_filter.append(Incomealloc.rentcode.ilike('%{}%'.format(memo)))
            moneyvals['memo'] = memo
        accdesc = request.form.get("accdesc") or "all accounts"
        if accdesc != "all accounts":
            money_filter.append(Money_account.accdesc.ilike('%{}%'.format(accdesc)))
            income_filter.append(Money_account.accdesc.ilike('%{}%'.format(accdesc)))
            moneyvals['accdesc'] = accdesc
        clearedval = request.form.get("cleared") or "all"
        moneyvals['cleared'] = clearedval
        if clearedval == "cleared":
            money_filter.append(Money_item.cleared == 1)
        elif clearedval == "uncleared":
            money_filter.append(Money_item.cleared == 0)
        catval = request.form.get("category") or "all categories"
        if catval != "all categories":
            money_filter.append(Money_category.cat_name == catval)
            if catval != "Jinn BACS income":
                income_filter.append(Income.id == 0)
        moneyvals['category'] = catval

    transitems = \
        Money_item.query.join(Money_account).join(Money_category) .with_entities(Money_item.id, Money_item.num,
                     Money_item.date, Money_item.payer, Money_item.amount, Money_item.memo,
                           Money_account.accdesc, Money_category.cat_name, Money_item.cleared) \
            .filter(*money_filter).union\
            (Income.query.join(Money_account).join(Incomealloc).with_entities(Income.id, literal("X").label('num'),
                  Income.date, Income.payer, Income.amount, Incomealloc.rentcode.label('memo'), Money_account.accdesc,
                      literal("BACS income").label('cat_name'), literal("1").label('cleared')) \
             .filter(*income_filter)) \
             .order_by(desc(Money_item.date), desc(Income.date), Money_item.memo, Incomealloc.rentcode).limit(100)

    accsums = Money_item.query.with_entities(func.samjinn.acc_balance(id, 1, date.today()).label('cbalance'),
                 func.samjinn.acc_balance(Money_account.id, 0, date.today()).label('ubalance')).filter().first()

    return accsums, moneyvals, transitems


def post_moneyaccount(id):
    # new moneyaccount:
    if id == 0:
        moneyacc = Money_account()
    else:
        # existing moneyaccount:
        moneyacc = Money_account.query.get(id)
    moneyacc.bankname = request.form.get("bankname")
    moneyacc.accname = request.form.get("accname")
    moneyacc.sortcode = request.form.get("sortcode")
    moneyacc.accnum = request.form.get("accnum")
    accdesc = request.form.get("accdesc")
    moneyacc.accdesc = accdesc
    db.session.add(moneyacc)
    db.session.flush()
    acc_id = moneyacc.id
    db.session.commit()

    return acc_id


def post_moneyitem(id):
    if id == 0:
        # new moneyitem:
        moneyitem = Money_item()
    else:
        # existing moneyitem:
        moneyitem = Money_item.query.get(id)
    moneyitem.num = request.form.get("number")
    moneyitem.date = request.form.get("paydate")
    moneyitem.amount = request.form.get("amount")
    moneyitem.payer = request.form.get("payer")
    bankaccount = request.form.get("bankaccount")
    bank_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == bankaccount).one()[0]
    moneyitem.bankacc_id = bank_id
    cleared = request.form.get("cleared")
    moneyitem.cleared = 1 if cleared == "cleared" else 0
    category = request.form.get("category")
    moneyitem.cat_id = \
        Money_category.query.with_entities(Money_category.id).filter \
            (Money_category.cat_name == category).one()[0]
    db.session.add(moneyitem)
    db.session.flush()
    bank_id = moneyitem.id
    db.session.commit()


    return bank_id


