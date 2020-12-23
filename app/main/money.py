from datetime import date
from flask import flash, redirect, url_for, request, session
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app import db
from app.main.functions import commit_to_database
from app.models import Income, Incomealloc, Money_account, Money_category, Money_item


def get_moneyaccount(id):
    if id == 0:
        moneyacc = Money_account()
        moneyacc.id = 0
    else:
        moneyacc = Money_account.query.filter(Money_account.id == id).one_or_none()

    return moneyacc


def get_moneydets():
    moneydets = Money_account.query.with_entities(Money_account.id, Money_account.bankname, Money_account.accname,
                  Money_account.sortcode, Money_account.accnum, Money_account.accdesc,
                           func.mjinn.acc_balance(Money_account.id, 1, date.today()).label('cbalance'),
                           func.mjinn.acc_balance(Money_account.id, 0, date.today()).label('ubalance')).all()

    accsums = Money_account.query.with_entities(func.mjinn.acc_total(1).label('cleared'),
                                            func.mjinn.acc_total(0).label('uncleared')).filter().first()

    return moneydets, accsums


def get_moneyitem(id):
    bankitem = Money_item.query.join(Money_account).join(Money_category).with_entities(Money_item.id, Money_item.num,
                Money_item.date, Money_item.payer, Money_item.amount, Money_item.memo,Money_account.accdesc,
                   Money_category.cat_name, Money_item.cleared).filter(Money_item.id == id).one_or_none()

    return bankitem


def get_moneyitems(id):
    money_filter = []
    income_filter = []
    values = {'accdesc': 'all accounts', 'payee': 'all', 'memo': 'all', 'category': 'all categories', 'cleared': 'all'}
    if id != 0:
        money_filter.append(Money_account.id == id)
        income_filter.append(Money_account.id == id)
        moneyacc = get_moneyaccount(id)
        values['accdesc'] = moneyacc.accdesc
    if request.method == "POST":
        payee = request.form.get("payee") or "all"
        if payee != "all":
            money_filter.append(Money_item.payer.ilike('%{}%'.format(payee)))
            income_filter.append(Income.payer.ilike('%{}%'.format(payee)))
            values['payee'] = payee
        memo = request.form.get("memo") or "all"
        if memo != "all":
            money_filter.append(Money_item.memo.ilike('%{}%'.format(memo)))
            income_filter.append(Incomealloc.rentcode.ilike('%{}%'.format(memo)))
            values['memo'] = memo
        accdesc = request.form.get("accdesc") or "all accounts"
        if accdesc != "all accounts":
            money_filter.append(Money_account.accdesc.ilike('%{}%'.format(accdesc)))
            income_filter.append(Money_account.accdesc.ilike('%{}%'.format(accdesc)))
            values['accdesc'] = accdesc
        clearedval = request.form.get("cleared") or "all"
        values['cleared'] = clearedval
        if clearedval == "cleared":
            money_filter.append(Money_item.cleared == 1)
        elif clearedval == "uncleared":
            money_filter.append(Money_item.cleared == 0)
            income_filter.append(Income.id == 0)
        catval = request.form.get("category") or "all categories"
        if catval != "all categories":
            money_filter.append(Money_category.cat_name == catval)
            if catval != "Jinn BACS income":
                income_filter.append(Income.id == 0)
        values['category'] = catval

    moneyitems = \
        Money_item.query.join(Money_account).join(Money_category) .with_entities(Money_item.id, Money_item.num,
                     Money_item.date, Money_item.payer, Money_item.amount, Money_item.memo,
                           Money_account.accdesc, Money_category.cat_name, Money_item.cleared) \
            .filter(*money_filter).union\
            (Income.query.join(Money_account).join(Incomealloc).with_entities(Income.id, literal("X").label('num'),
                  Income.date, Income.payer, Income.amount, Incomealloc.rentcode.label('memo'), Money_account.accdesc,
                      literal("BACS income").label('cat_name'), literal("1").label('cleared')) \
             .filter(*income_filter)) \
             .order_by(desc(Money_item.date), desc(Income.date), Money_item.memo, Incomealloc.rentcode).limit(100)

    accsums = Money_item.query.with_entities(func.mjinn.acc_balance(id, 1, date.today()).label('cbalance'),
                 func.mjinn.acc_balance(Money_account.id, 0, date.today()).label('ubalance')).filter().first()

    return accsums, moneyitems, values


def get_money_options():
    # return options for each multiple choice control in money_edit and money_filter pages
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs.insert(0, "all accounts")
    cats = [value for (value,) in Money_category.query.with_entities(Money_category.cat_name).all()]
    cats.insert(0, "all categories")
    cleareds = ["all", "cleared", "uncleared"]

    return bankaccs, cats, cleareds


def post_moneyaccount(id):
    if id == 0:
        moneyacc = Money_account()
        moneyacc.id = 0
    else:
        moneyacc = Money_account.query.get(id)
    moneyacc.bankname = request.form.get("bankname")
    moneyacc.accname = request.form.get("accname")
    moneyacc.sortcode = request.form.get("sortcode")
    moneyacc.accnum = request.form.get("accnum")
    moneyacc.accdesc = request.form.get("accdesc")
    db.session.add(moneyacc)
    db.session.commit()
    id_ = moneyacc.id

    return id_


def post_moneyitem(id, action):
    if action == "edit":
        bankitem = Money_item.query.get(id)
    else:
        bankitem = Money_item()
    bankitem.num = request.form.get("num")
    bankitem.date = request.form.get("date")
    bankitem.amount = request.form.get("amount")
    bankitem.payer = request.form.get("payer")
    accdesc = request.form.get("accdesc")
    bankitem.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == accdesc).one()[0]
    cleared = request.form.get("cleared")
    bankitem.cleared = 1 if cleared == "cleared" else 0
    cat = request.form.get("category")
    bankitem.cat_name = \
        Money_category.query.with_entities(Money_category.id).filter \
            (Money_category.cat_name == cat).one()[0]
    db.session.add(bankitem)
    db.session.commit()
    id_ = bankitem.id

    return id_


