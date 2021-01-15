from flask import request
from sqlalchemy import desc
from app import db
from app.models import Charge, Chargetype, Income, Incomealloc, Landlord, Money_account, Rent, Typepayment


def get_incomes(id):
    #possible bank account id from money and possible param rentid as arg from rent screen
    qfilter = []
    incomevals = {
        'bankacc': 'all accounts',
        'payer': '',
        'rentcode': '',
        'rentid': 0,
        'paytype': 'all payment types'
    }
    if id != 0:
        # first deal with bank account id being passed from money app
        qfilter.append(Money_account.id == id)
        bankacc = Money_account.query.filter(Money_account.id == id).one_or_none()
        incomevals['bankacc'] = bankacc.accdesc
    if request.method == "POST":
        payer = request.form.get("payer") or ""
        if payer and payer != "" and payer != "all payers":
            qfilter.append(Income.payer.ilike('%{}%'.format(payer)))
            incomevals['payer'] = payer
        rentcode = request.form.get("rentcode") or ""
        if rentcode and rentcode != "" and rentcode != "all rentcodes":
            qfilter.append(Incomealloc.rentcode.startswith([rentcode]))
            incomevals['rentcode'] = rentcode
        bankacc = request.form.get("bankacc") or ""
        if bankacc and bankacc != "" and bankacc != "all accounts":
            qfilter.append(Money_account.accdesc == bankacc)
            incomevals['bankacc'] = bankacc
        paytype = request.form.get("paytype") or ""
        if paytype and paytype != "" and paytype != "all payment types":
            qfilter.append(Typepayment.paytypedet == paytype)
            incomevals['paytype'] = paytype
    else:
        # now deal with rentid coming from the rent screen
        rentid = int(request.args.get('rentid', "0", type=str))
        if rentid != 0:
            qfilter.append(Incomealloc.rent_id == rentid)
            incomevals['rentid'] = rentid

    incomes = Incomealloc.query.join(Income).join(Chargetype).join(Money_account).join(Typepayment) \
            .with_entities(Income.id, Income.date, Incomealloc.rent_id, Incomealloc.rentcode, Income.amount,
                           Income.payer, Money_account.accdesc, Chargetype.chargedesc, Typepayment.paytypedet) \
            .filter(*qfilter).order_by(desc(Income.date)).limit(50).all()

    return incomes, incomevals


def get_income_dict(type):
    # return options for multiple choice controls in income object
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs_all = bankaccs
    bankaccs_all.insert(0, "all accounts")
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]
    paytypes_all = paytypes
    paytypes_all.insert(0, "all payment types")
    income_dict = {
        "bankaccs": bankaccs,
        "bankaccs_all": bankaccs_all,
        "paytypes": paytypes,
        "paytypes_all": paytypes_all
    }
    if type == "enhanced":
        chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
        landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
        income_dict["chargedescs"] = chargedescs
        income_dict["landlords"] = landlords

    return income_dict


def get_income_(id):
    income = Income.query.join(Money_account).join(Typepayment).with_entities(Income.id, Income.date, Income.amount,
              Income.payer, Typepayment.paytypedet, Money_account.accdesc).filter(Income.id == id).one_or_none()

    incomeallocs = Incomealloc.query.join(Chargetype).join(Rent).with_entities(Incomealloc.id,
                    Incomealloc.income_id, Rent.rentcode, Incomealloc.amount.label("alloctot"),
                    Chargetype.chargedesc).filter(Incomealloc.income_id == id).all()

    return income, incomeallocs


def post_income_(id, action):
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
