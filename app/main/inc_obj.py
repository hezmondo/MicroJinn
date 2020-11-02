import datetime
from flask import flash, redirect, request
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app import db
from app.main.functions import commit_to_database
from app.models import Charge, Chargetype, Income, Incomealloc, Landlord, Money_account, Rent, Typepayment


def get_incomes(rentid):
    qfilter = []
    payer = request.form.get("payer") or ""
    if payer and payer != "":
        qfilter.append(Income.payer.ilike('%{}%'.format(payer)))
    rentcode = request.form.get("rentcode") or ""
    if rentcode and rentcode != "":
        qfilter.append(Incomealloc.rentcode.startswith([rentcode]))
    accountdesc = request.form.get("accountdesc") if request.method == "POST" else ""
    paymtype = request.form.get("paymtype") if request.method == "POST" else ""
    if accountdesc and accountdesc != "" and accountdesc != "all accounts":
        qfilter.append(Money_account.accdesc == accountdesc)
    if paymtype and paymtype != ""and paymtype != "all payment types":
        qfilter.append(Typepayment.paytypedet == paymtype)
    if rentid > 0:
        qfilter.append(Incomealloc.rent_id == rentid)

    incomes = Incomealloc.query.join(Income).join(Chargetype).join(Money_account).join(Typepayment) \
            .with_entities(Income.id, Income.date, Incomealloc.rentcode, Income.amount, Income.payer,
                           Money_account.accdesc, Chargetype.chargedesc, Typepayment.paytypedet) \
            .filter(*qfilter).order_by(desc(Income.date)).limit(50).all()

    return incomes


def get_inc_options():
    # return options for multiple choice controls in income
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs.insert(0, "all accounts")
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]
    paytypes.insert(0, "all payment types")

    return bankaccs, paytypes


def get_incobj(id):
    income = Income.query.join(Money_account).join(Typepayment).with_entities(Income.id, Income.date, Income.amount,
              Income.payer, Typepayment.paytypedet, Money_account.accdesc).filter(Income.id == id).one_or_none()

    incomeallocs = Incomealloc.query.join(Chargetype).join(Rent).with_entities(Incomealloc.id,
                    Incomealloc.income_id, Rent.rentcode, Incomealloc.amount.label("alloctot"),
                    Chargetype.chargedesc).filter(Incomealloc.income_id == id).all()

    return income, incomeallocs


def get_incobj_options():
    # return options for multiple choice controls in income_object
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]

    return bankaccs, chargedescs, landlords, paytypes


def get_incobj_post(id):
    post = Rent.query.join(Landlord).join(Money_account).join(Charge).with_entities(Rent.rentcode,
                Rent.arrears, Rent.datecode, Rent.lastrentdate, Rent.landlord_id,
                func.mjinn.next_date(Rent.lastrentdate, Rent.freq_id, 1).label('nextrentdate'),
                func.sum(Charge.chargebalance).label('chargetot'),
                Rent.rentpa, Rent.tenantname, Rent.freq_id, Money_account.accdesc) \
                .filter(Rent.id == id) \
                .one_or_none()
    arrears = post.arrears
    today = datetime.date.today()
    allocs = Charge.query.join(Chargetype).join(Rent).join(Landlord).with_entities(Rent.rentcode, Charge.id,
                   Chargetype.chargedesc, Charge.chargebalance, Landlord.landlordname).filter(Charge.rent_id == id).all()
    if post.chargetot and post.chargetot > 0:
        post_tot = arrears + post.chargetot
    elif arrears > 0:
        post_tot = arrears
    else:
        post_tot = post.rentpa

    return allocs, post, post_tot, today


def post_inc_obj(id, action):
    # this object comprises 1 income record plus 1 or more incomealloc records. First, we do the income record
    if action == "edit":
        income = Income.query.get(id)
    else:
        income = Income()
    income.paydate = request.form.get("paydate")
    income.amount = request.form.get("amount")
    income.payer = request.form.get("payer")
    bankacc = request.form.get("bankacc")
    income.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter(Money_account.accdesc == bankacc).one()[0]
    paytype = request.form.get("paytype")
    income.paytype_id = \
        Typepayment.query.with_entities(Typepayment.id).filter(Typepayment.paytypedet == paytype).one()[0]
    # having set the column values, we add this single income record to the db session
    db.session.add(income)
    # now we get the income allocations from the request form to post 1 or more records to the incomealloc table
    if action == "edit":
        allocs = zip(request.form.getlist("incall_id"), request.form.getlist('rentcode'),
                         request.form.getlist('alloctot'), request.form.getlist("chargedesc"))
        for incall_id, rentcode, alloctot, chargedesc in allocs:
            print(incall_id, rentcode, alloctot, chargedesc)
            if alloctot == "0" or alloctot == "0.00":
                continue
            if incall_id and int(incall_id) > 0:
                incalloc = Incomealloc.query.get(int(incall_id))
            else:
                incalloc = Incomealloc()
            incalloc.rentcode = rentcode
            incalloc.amount = alloctot
            print(incalloc.amount)
            incalloc.chargetype_id = \
                Chargetype.query.with_entities(Chargetype.id).filter(Chargetype.chargedesc == chargedesc).one()[0]
            print(incalloc.chargetype_id)
            incalloc.landlord_id = \
                Landlord.query.join(Rent).with_entities(Landlord.id).filter(Rent.rentcode == rentcode).one()[0]
            # having set the column values, we add each incomealloc record to the db session (using the ORM relationship)
            income.incomealloc_income.append(incalloc)
    else:
        allocs = zip(request.form.getlist('rentcode'), request.form.getlist("c_id"), request.form.getlist("chargedesc"),
                     request.form.getlist('alloctot'), request.form.getlist('landlord'))
        for rentcode, alloctot, c_id, chargedesc, landlord in allocs:
            print(rentcode, alloctot, c_id, chargedesc, landlord)
            if alloctot == "0" or alloctot == "0.00":
                continue
            incalloc = Incomealloc()
            incalloc.rentcode = rentcode
            incalloc.amount = alloctot
            print(incalloc.amount)
            incalloc.chargetype_id = \
                Chargetype.query.with_entities(Chargetype.id).filter(Chargetype.chargedesc == chargedesc).one()[0]
            print(incalloc.chargetype_id)
            incalloc.landlord_id = \
                Landlord.query.with_entities(Landlord.id).filter(Landlord.landlordname == landlord).one()[0]
            # having set the column values, we add each incomealloc record to the db session (using the ORM relationship)
            income.incomealloc_income.append(incalloc)
            # now we have to deal with updating or deleting existing charges
            if c_id  and c_id > 0:
                d_charge = Charge.query.get(c_id)
                db.session.delete(d_charge)

    # having added the income record and all incomealloc records to the db session, we now attempt a commit
    db.session.commit()
    # in case of a new record, we need to find and return the new id, to display the new (or updated) income object
    id_ = income.id

    return id_
