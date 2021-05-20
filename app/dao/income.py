from flask import request
from sqlalchemy import desc
from sqlalchemy.orm import joinedload, load_only
from app import db
from app.models import ChargeType, Income, IncomeAlloc, MoneyAcc, Rent
from app.modeltypes import PayTypes
from app.dao.database import commit_to_database


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


def get_incomes_sql(sql):  # simple filtered rents for main rents page using raw sql
    return db.session.execute(sql).fetchall()


# def get_incomes_main(filtr, runsize):    # filtered incomedata for main income page
#     return db.session.query(Income).join(MoneyAcc).join(Income.allocs) \
#         .options(load_only('id', 'date', 'amount', 'payer', 'paytype_id'),
#            joinedload('money_account').load_only('acc_desc'),
#            joinedload(Income.allocs).load_only('rentcode'),
#            db.contains_eager(Income.allocs)) \
#         .filter(*filtr).limit(runsize).all()


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
    income.paytype_id = PayTypes.get_id(paytype)
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
