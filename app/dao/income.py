from flask import request
from sqlalchemy import desc
from app import db
from app.models import ChargeType, Income, IncomeAlloc, Landlord, MoneyAcc, Rent
from app.dao.common import get_charge_types, PayTypes
from app.dao.database import commit_to_database


def get_incomes(acc_id):
    # display postings for all bank accounts if accid = 0 and pick up rent_id as arg from rent screen
    rent_id = int(request.args.get('rent_id', "0", type=str))
    qfilter = []
    incomevals = {
        'acc_desc': 'all accounts',
        'payer': '',
        'rentcode': '',
        'rent_id': rent_id,
        'paytype': 'all payment types'
    }
    if acc_id != 0:
        # first deal with bank account id being passed from money app
        qfilter.append(MoneyAcc.id == id)
        acc_desc = MoneyAcc.query.filter(MoneyAcc.id == id).one_or_none()
        incomevals['acc_desc'] = acc_desc.acc_desc
    # now deal with the user clicking search button to filter ibcome postings
    if request.method == "POST":
        payer = request.form.get("payer") or ""
        if payer and payer != "" and payer != "all payers":
            qfilter.append(Income.payer.ilike('%{}%'.format(payer)))
            incomevals['payer'] = payer
        rentcode = request.form.get("rentcode") or ""
        if rentcode and rentcode != "" and rentcode != "all rentcodes":
            qfilter.append(IncomeAlloc.rentcode.startswith([rentcode]))
            incomevals['rentcode'] = rentcode
        acc_desc = request.form.get("acc_desc") or ""
        if acc_desc and acc_desc != "" and acc_desc != "all accounts":
            qfilter.append(MoneyAcc.acc_desc == acc_desc)
            incomevals['acc_desc'] = acc_desc
        paytype = request.form.get("paytype") or ""
        if paytype and paytype != "" and paytype != "all payment types":
            qfilter.append()
            incomevals['paytype'] = paytype
    else:
        # now deal with rent_id coming from the rent screen
        if rent_id != 0:
            qfilter.append(IncomeAlloc.rent_id == rent_id)
            incomevals['rent_id'] = rent_id
    incomes = IncomeAlloc.query.join(Income).join(ChargeType).join(MoneyAcc) \
            .with_entities(Income.id, Income.date, IncomeAlloc.rent_id, IncomeAlloc.rentcode, Income.amount,
                           Income.paytype_id, Income.payer, MoneyAcc.acc_desc, ChargeType.chargedesc) \
            .filter(*qfilter).order_by(desc(Income.date)).limit(50).all()
    # for income in incomes:
    #     income.paytype = get_paytype(income.paytype_id)
    return incomes, incomevals


def get_income_dict(type):
    # return options for multiple choice controls in income object
    acc_descs = [value for (value,) in MoneyAcc.query.with_entities(MoneyAcc.acc_desc).all()]
    acc_descs_all = acc_descs
    acc_descs_all.insert(0, "all accounts")
    paytypes = PayTypes.names()
    paytypes_all = paytypes
    paytypes_all.insert(0, "all payment types")
    income_dict = {
        "acc_descs": acc_descs,
        "acc_descs_all": acc_descs_all,
        "paytypes": paytypes,
        "paytypes_all": paytypes_all
    }
    if type == "enhanced":
        chargedescs = [chargetype.chargedesc for chargetype in get_charge_types()]

        chargedescs = [value for (value,) in ChargeType.query.with_entities(ChargeType.chargedesc).all()]
        landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
        income_dict["chargedescs"] = chargedescs
        income_dict["landlords"] = landlords
    return income_dict


def get_income_(income_id):
    income = Income.query \
        .join(MoneyAcc) \
        .with_entities(Income.id, Income.date, Income.amount, Income.paytype_id, Income.payer, MoneyAcc.acc_desc) \
        .filter(Income.id == income_id).one_or_none()
    incomeallocs = IncomeAlloc.query.join(ChargeType).join(Rent).with_entities(IncomeAlloc.id,
                                                                               IncomeAlloc.income_id, Rent.rentcode, IncomeAlloc.amount.label("alloctot"),
                                                                               ChargeType.chargedesc).filter(IncomeAlloc.income_id == income_id).all()
    return income, incomeallocs


def get_income_item(rent_id, income_id=0):
    if income_id == 0:           # return most recent income posting for this rent_id
        income_item = Income.query. \
            join(IncomeAlloc) \
            .with_entities(Income.id, Income.paytype_id, Income.payer, Income.date.label("paydate"), Income.amount.label("payamount")) \
            .filter(IncomeAlloc.rent_id == rent_id).order_by(desc(Income.date)).limit(1).one_or_none()
        # income_id = income_item.id
    else:           # return income posting for a specific income id
        income_item = Income.query \
            .join(IncomeAlloc) \
            .with_entities(Income.id, Income.paytype_id, Income.payer, Income.date.label("paydate"), Income.amount.label("payamount")) \
            .filter(Income.id == income_id).first()
    # allocdata = IncomeAlloc.join(ChargeType).with_entities(IncomeAlloc.id, IncomeAlloc.income_id,
    #                     IncomeAlloc.rentcode, IncomeAlloc.amount.label("alloctot"),
    #                     ChargeType.chargedesc).filter(IncomeAlloc.income_id == income_id).all()
    allocdata = None
    return income_item, allocdata


def post_income_(income_id):
    # this object comprises 1 income record plus 1 or more incomealloc records. First, we do the income record
    if income_id == 0:
        income = Income()
    else:
        income = Income.query.get(income_id)
    income.paydate = request.form.get("paydate")
    income.amount = request.form.get("amount")
    income.payer = request.form.get("payer")
    acc_desc = request.form.get("acc_desc")
    income.acc_id = \
        MoneyAcc.query.with_entities(MoneyAcc.id).filter(MoneyAcc.acc_desc == acc_desc).one()[0]
    paytype = request.form.get("paytype")
    income.paytype_id = get_paytype_id(paytype)
    # having set the column values, we add this single income record to the db session
    db.session.add(income)
    # next bit of code needs complete restructuring as bonkers!
    # now we get the income allocations from the request form to post 1 or more records to the incomealloc table
    # if income_id == 0:
    #     allocs = zip(request.form.getlist('rentcode'), request.form.getlist("c_id"),
    #     request.form.getlist("chargedesc"), request.form.getlist('alloctot'), request.form.getlist('landlord'))
    #     for rentcode, alloctot, c_id, chargedesc, landlord in allocs:
    #         print(rentcode, alloctot, c_id, chargedesc, landlord)
    #         if alloctot == "0" or alloctot == "0.00":
    #             continue
    #         incalloc = IncomeAlloc()
    #         incalloc.rentcode = rentcode
    #         incalloc.amount = alloctot
    #         print(incalloc.amount)
    #         incalloc.chargetype_id = \
    #             ChargeType.query.with_entities(ChargeType.id).filter(ChargeType.chargedesc == chargedesc).one()[0]
    #         print(incalloc.chargetype_id)
    #         incalloc.landlord_id = \
    #             Landlord.query.with_entities(Landlord.id).filter(Landlord.name == landlord).one()[0]
    #         # having set the column values, we add each incomealloc record to the session using the ORM relationship
    #         income.incomealloc_income.append(incalloc)
    #         # now we have to deal with updating or deleting existing charges
    #         if c_id  and c_id > 0:
    #             d_charge = Charge.query.get(c_id)
    #             db.session.delete(d_charge)
    #
    #     else:
    #         allocs = zip(request.form.getlist("incall_id"), request.form.getlist('rentcode'),
    #                          request.form.getlist('alloctot'), request.form.getlist("chargedesc"))
    #         for incall_id, rentcode, alloctot, chargedesc in allocs:
    #             print(incall_id, rentcode, alloctot, chargedesc)
    #             if alloctot == "0" or alloctot == "0.00":
    #                 continue
    #             if incall_id and int(incall_id) > 0:
    #                 incalloc = IncomeAlloc.query.get(int(incall_id))
    #             else:
    #                 incalloc = IncomeAlloc()
    #             incalloc.rentcode = rentcode
    #             incalloc.amount = alloctot
    #             print(incalloc.amount)
    #             incalloc.chargetype_id = \
    #                 ChargeType.query \
    #                 .with_entities(ChargeType.id) \
    #                 .filter(ChargeType.chargedesc == chargedesc).one()[0]
    #             print(incalloc.chargetype_id)
    #             incalloc.landlord_id = \
    #                 Landlord.query.join(Rent).with_entities(Landlord.id).filter(Rent.rentcode == rentcode).one()[0]
    #             # having set the column values, we add each incomealloc record to the db session
    #             (using the ORM relationship)
    #             income.incomealloc_income.append(incalloc)
    # having added the income record and all incomealloc records to the db session, we now attempt a commit
    commit_to_database()
