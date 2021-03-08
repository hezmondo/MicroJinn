import datetime
from datetime import date
from flask import request
from sqlalchemy import desc, func, literal
from app import db
from app.dao.database import commit_to_database
from app.models import Income, IncomeAlloc, MoneyAcc, MoneyCat, MoneyItem


def get_money_acc(acc_id):
    # get values for a single account and deal with post
    if acc_id == 0:
        moneyacc = MoneyAcc()
        moneyacc.id = 0
    else:
        moneyacc = MoneyAcc.query.filter(MoneyAcc.id == acc_id).one_or_none()
    return moneyacc


def get_moneydets():
    # get values to list all accounts on the money home page, with totals at the bottom
    moneydets = MoneyAcc.query \
        .with_entities(MoneyAcc.id, MoneyAcc.bank_name, MoneyAcc.acc_name, MoneyAcc.sort_code,
                       MoneyAcc.acc_num, MoneyAcc.acc_desc,
                       func.mjinn.acc_balance(MoneyAcc.id, 1, date.today()).label('cbalance'),
                       func.mjinn.acc_balance(MoneyAcc.id, 0, date.today()).label('ubalance')).all()
    accsums = MoneyAcc.query.with_entities(func.mjinn.acc_total(1).label('cleared'),
                                           func.mjinn.acc_total(0).label('uncleared')).filter().first()
    return accsums, moneydets


def get_moneydict(type="basic"):
    # return options for multiple choice controls in money_item and money_items pages
    acc_descs = [value for (value,) in MoneyAcc.query.with_entities(MoneyAcc.acc_desc).all()]
    cats = [value for (value,) in MoneyCat.query.with_entities(MoneyCat.cat_name).all()]
    cleareds = ["cleared", "uncleared"]
    money_dict = {
        "acc_descs": acc_descs,
        "cats": cats,
        "cleareds": cleareds,
    }
    if type == "plus_all":
        money_dict["acc_descs"].insert(0, "all accounts")
        money_dict["cats"].insert(0, "all categories")
        money_dict["cleareds"].insert(0, "all cleareds")
    return money_dict


def get_money_item(money_item_id):
    if money_item_id == 0:
        money_item = get_money_item_new()
        cleared = "cleared"
    else:
        money_item = MoneyItem.query.join(MoneyAcc).join(MoneyCat).with_entities(MoneyItem.id,
                                                                                 MoneyItem.num, MoneyItem.date, MoneyItem.payer, MoneyItem.amount, MoneyItem.memo,
                                                                                 MoneyAcc.id.label("acc_id"), MoneyAcc.acc_desc, MoneyCat.cat_name,
                                                                                 MoneyItem.cleared) \
            .filter(MoneyItem.id == money_item_id).one_or_none()

        cleared = "cleared" if money_item.cleared == 1 else "uncleared"
    return money_item, cleared


def get_money_item_new():
    acc_id = request.args.get('acc_id', 1, type=int)
    acc_desc = request.args.get('acc_desc', "Santander RHDM", type=str)
    money_item = {'id': 0,
                  'num': 0,
                  'date': datetime.date.today(),
                  'acc_id': acc_id,
                  'acc_desc': acc_desc,
                  'cat_name': 'Fuel'
                  }
    return money_item


def get_money_items(acc_id): # we assemble income items and money items into one display - tricky
    money_filter = []
    income_filter = [Income.paytype_id != 1] # we do not want cheque income displayed, as not cleared income
    moneyvals= {'acc_id': acc_id, 'acc_desc': 'all accounts'}
    if acc_id != 0: # filter for money account id, otherwise items for all accounts
        money_filter.append(MoneyAcc.id == acc_id)
        income_filter.append(MoneyAcc.id == acc_id)
        account = MoneyAcc.query.filter(MoneyAcc.id == acc_id).one_or_none()
        moneyvals['acc_desc'] = account.acc_desc
    if request.method == "POST":
        payee = request.form.get("payee") or "all"
        if payee != "all":
            money_filter.append(MoneyItem.payer.ilike('%{}%'.format(payee)))
            income_filter.append(Income.payer.ilike('%{}%'.format(payee)))
            moneyvals['payee'] = payee
        memo = request.form.get("memo") or "all"
        if memo != "all":
            money_filter.append(MoneyItem.memo.ilike('%{}%'.format(memo)))
            income_filter.append(IncomeAlloc.rentcode.ilike('%{}%'.format(memo)))
            moneyvals['memo'] = memo
        acc_desc = request.form.get("acc_desc") or "all accounts"
        if acc_desc != "all accounts":
            money_filter.append(MoneyAcc.acc_desc.ilike('%{}%'.format(acc_desc)))
            income_filter.append(MoneyAcc.acc_desc.ilike('%{}%'.format(acc_desc)))
            moneyvals['acc_desc'] = acc_desc
        clearedval = request.form.get("cleared") or "all"
        moneyvals['cleared'] = clearedval
        if clearedval == "cleared":
            money_filter.append(MoneyItem.cleared == 1)
        elif clearedval == "uncleared":
            money_filter.append(MoneyItem.cleared == 0)
        catval = request.form.get("category") or "all categories"
        if catval != "all categories":
            money_filter.append(MoneyCat.cat_name == catval)
            if catval != "Jinn BACS income":
                income_filter.append(Income.id == 0)
        moneyvals['category'] = catval
    transitems = \
        MoneyItem.query.join(MoneyAcc) \
            .join(MoneyCat) \
            .with_entities(MoneyItem.id, MoneyItem.num, MoneyItem.date, MoneyItem.payer, MoneyItem.amount,
                           MoneyItem.memo, MoneyAcc.acc_desc, MoneyCat.cat_name, MoneyItem.cleared) \
            .filter(*money_filter) \
            .union_all(
            (Income.query.join(MoneyAcc)
             .join(IncomeAlloc)
             .with_entities(Income.id, literal("X").label('num'), Income.date, Income.payer, Income.amount,
                            IncomeAlloc.rentcode.label('memo'), MoneyAcc.acc_desc,
                            literal("BACS income").label('cat_name'), literal("1").label('cleared'))
             .filter(*income_filter))) \
             .order_by(desc(MoneyItem.date), desc(Income.date), MoneyItem.memo, IncomeAlloc.rentcode).limit(100)
    accsums = MoneyItem.query.with_entities\
        (func.mjinn.acc_balance(acc_id, 1, date.today()).label('cbalance'),
         func.mjinn.acc_balance(MoneyAcc.id, 0, date.today()).label('ubalance')).filter().first()
    return accsums, moneyvals, transitems


def post_money_acc(acc_id):
    # new moneyaccount:
    if acc_id == 0:
        moneyacc = MoneyAcc()
    else:
        # existing moneyaccount:
        moneyacc = MoneyAcc.query.get(acc_id)
    moneyacc.bank_name = request.form.get("bank_name")
    moneyacc.acc_name = request.form.get("acc_name")
    moneyacc.sort_code = request.form.get("sort_code")
    moneyacc.acc_num = request.form.get("acc_num")
    acc_desc = request.form.get("acc_desc")
    moneyacc.acc_desc = acc_desc
    db.session.add(moneyacc)
    db.session.flush()
    acc_id = moneyacc.id
    commit_to_database()
    return acc_id


def post_money_item(money_item_id):
    if money_item_id == 0:        # new money item:
        money_item = MoneyItem()
    else:        # existing money_item:
        money_item = MoneyItem.query.get(money_item_id)
    money_item.num = request.form.get("number")
    money_item.date = request.form.get("paydate")
    money_item.amount = request.form.get("amount")
    money_item.payer = request.form.get("payer")
    acc_desc = request.form.get("acc_desc")
    acc_id = \
        MoneyAcc.query.with_entities(MoneyAcc.id).filter \
            (MoneyAcc.acc_desc == acc_desc).one()[0]
    money_item.acc_id = acc_id
    cleared = request.form.get("cleared")
    money_item.cleared = 1 if cleared == "cleared" else 0
    category = request.form.get("category")
    cat_id = \
        MoneyCat.query.with_entities(MoneyCat.id).filter \
            (MoneyCat.cat_name == category).one()[0]
    money_item.cat_id = cat_id
    db.session.add(money_item)
    db.session.flush()
    money_item = money_item.id
    commit_to_database()
    return money_item


