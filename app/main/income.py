from flask import request
from app.dao.charge import get_charge_descs
from app.dao.money import get_acc_desc, get_acc_descs, get_acc_id
from app.dao.income import get_incomes_sql
from app.modeltypes import PayTypes


def get_incomes(acc_id):
    # display postings for all bank accounts if accid = 0 and pick up rent_id as arg from rent screen
    rent_id = int(request.args.get('rent_id', "0", type=str))
    incomevals = {
        'acc_desc': ['all accounts'],
        'payer': '',
        'rentcode': '',
        'rent_id': rent_id,
        'paytype': ['all payment types']
    }
    if acc_id != 0:
        # first deal with bank account id being passed from money app
        incomevals['acc_id'] = acc_id
        acc_desc = get_acc_desc(acc_id)
        incomevals['acc_desc'] = acc_desc
    # now deal with the user clicking search button to filter income postings
    if request.method == "POST":
        incomevals['payer'] = request.form.get("payer") or ""
        incomevals['rentcode'] = request.form.get("rentcode") or ""
        incomevals['acc_desc'] = request.form.getlist("acc_desc") or ['all accounts']
        incomevals['paytype'] = request.form.getlist("paytype") or ['all payment types']
    sql = income_sql_basic() + income_sql_plus(incomevals)
    incomes = get_incomes_sql(sql)

    return incomes, incomevals


def get_income_dict(type):
    # return options for multiple choice controls in income object
    acc_descs = get_acc_descs()
    acc_descs_all = acc_descs
    acc_descs_all.insert(0, "all accounts")
    income_dict = {
        "acc_descs": acc_descs,
        "acc_descs_all": acc_descs_all,
    }
    if type == "enhanced":
        chargedescs = get_charge_descs()
        income_dict["chargedescs"] = chargedescs
    return income_dict


def income_sql_basic():
    return """ SELECT i.id, i.date, i.amount, i.payer, i.paytype_id, m.acc_desc, a.rentcode
                FROM income i 
                LEFT JOIN money_account m
                ON m.id = i.acc_id
                INNER JOIN incomealloc a
                ON a.income_id = i.id """


def income_sql_plus(dict):
    # now deal with rent_id coming from the rent screen
    rentid_sql = " a.rent_id = {} ".format(dict.get('rent_id')) if dict.get('rent_id') != 0 else ""
    payer_sql = " i.payer LIKE '%{}%' ".format(dict.get('payer')) if dict.get('payer') else ""
    rentcode_sql = " a.rentcode LIKE '{}%' ".format(dict.get('rentcode')) if dict.get('rentcode') else ""
    accids = []
    if dict.get('acc_desc') and dict.get('acc_desc') != ["all accounts"]:
        for i in range(len(dict.get('acc_desc'))):
            accids.append(get_acc_id(dict.get('acc_desc')[i]))
    accid_sql = " m.id IN (%s) " % tuple(accids) if accids else ""
    ptids = []
    if dict.get('paytype') and dict.get('paytype') != ["all payment types"]:
        for i in range(len(dict.get('paytype'))):
            ptids.append(PayTypes.get_id(dict.get('paytype')[i]))
    paytype_sql = " i.paytype_id IN (%s) " % tuple(ptids) if ptids else ""
    sql2 = " AND " \
        .join([sql for sql in [rentid_sql, rentcode_sql, payer_sql, accid_sql, paytype_sql] if sql])
    sql2 = "WHERE " + sql2 + "GROUP BY i.id ORDER BY i.date desc LIMIT 50 " \
                        if sql2 else "GROUP BY i.id ORDER BY i.date desc LIMIT 50 "

    return sql2
