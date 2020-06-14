import json
from app import db
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import flash, redirect, url_for, request
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app.models import Agent, Charge, Chargetype, Date_f2, Date_f4, Extmanager, Extrent, Income, Incomealloc, \
    Jstore, Landlord, Loan, Loan_statement, Manager, Money_category, Money_item, \
    Property, Rent, Rental, Rental_statement, Typeactype, \
    Typeadvarr, Money_account, Typedeed, Typefreq, Typemailto, Typepayment, Typeprdelivery, Typeproperty, \
    Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def get_agent(id):
    agent = Agent.query.filter(Agent.id == id).one_or_none()

    return agent


def get_agents():
    agd = request.form.get("address") or ""
    age = request.form.get("email") or ""
    agn = request.form.get("notes") or ""
    agents = Agent.query.filter(Agent.agdetails.ilike('%{}%'.format(agd)), Agent.agemail.ilike('%{}%'.format(age)),
                    Agent.agnotes.ilike('%{}%'.format(agn))).all()

    return agents


def get_charge(id):
    charge = \
        Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
               Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
                .filter(Charge.id == id).one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]

    return charge, chargedescs


def get_charges(rentcode):
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        cdt = request.form.get("chargedetails") or ""
    else:
        rcd = rentcode if rentcode else ""
        cdt = ""
    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                     Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(Rent.rentcode.startswith([rcd]), Charge.chargedetails.ilike('%{}%'.format(cdt))) \
            .all()

    return charges


def get_emailaccounts():
    emailaccs = Emailaccount.query.all()

    return emailaccs


def get_emailaccount(id):
    emailacc = Emailaccount.query.filter(Emailaccount.id == id).one_or_none()

    return emailacc


def get_externalrent(id):
    externalrent = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.id == id) \
                .one_or_none()

    return externalrent


def get_headrents():
    headrents = None

    return headrents


def get_incomealloc(id):
    income = \
        Income.query.join(Money_account) \
            .join(Typepayment) \
            .with_entities(Income.id, Income.date, Income.amount, Income.payer,
                           Typepayment.paytypedet, Money_account.accdesc) \
            .filter(Income.id == id) \
            .one_or_none()
    # if income is None:
    #     flash('Invalid income id')
    #     return redirect('/income')
    incomeallocs = \
        Incomealloc.query.join(Landlord) \
            .join(Chargetype) \
            .with_entities(Incomealloc.id, Incomealloc.income_id, Incomealloc.alloc_id, Incomealloc.rentcode,
                           Incomealloc.amount, Landlord.name, Chargetype.chargedesc) \
            .filter(Incomealloc.income_id == id) \
            .all()

    return income, incomeallocs


def get_incomeitems():
    qfilter = []
    payer = request.form.get("payer") or ""
    if payer and payer != "":
        qfilter.append(Income.payer.ilike('%{}%'.format(payer)))
    rentcode = request.form.get("rentcode") or ""
    if rentcode and rentcode != "":
        qfilter.append(Incomealloc.rentcode.startswith([rentcode]))
    accountdesc = request.form["accountdesc"] if request.method == "POST" else ""
    paymtype = request.form["paymtype"] if request.method == "POST" else ""
    if accountdesc and accountdesc != "" and accountdesc != "all accounts":
        qfilter.append(Money_account.accdesc == accountdesc)
    if paymtype and paymtype != ""and paymtype != "all payment types":
        qfilter.append(Typepayment.paytypedet == paymtype)

    incomeitems = \
        Incomealloc.query.join(Income) \
            .join(Chargetype) \
            .join(Money_account) \
            .join(Typepayment) \
            .with_entities(Income.id, Income.date, Incomealloc.rentcode, Income.amount, Income.payer,
                           Money_account.accdesc, Chargetype.chargedesc, Typepayment.paytypedet) \
            .filter(*qfilter).order_by(desc(Income.date)) \
            .limit(50).all()

    return incomeitems


def get_incomeoptions():
    # return options for multiple choice controls in income
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs.insert(0, "all accounts")
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]
    paytypes.insert(0, "all payment types")

    return bankaccs, paytypes


def get_incomeitemoptions():
    # return options for multiple choice controls in income_item
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]

    return bankaccs, chargedescs, landlords, paytypes


def get_landlord(id):
    landlord = Landlord.query.join(Manager).join(Emailaccount).join(Money_account).with_entities(Landlord.id,
                 Landlord.name, Landlord.addr, Landlord.taxdate, Manager.name.label("manager"),
                     Emailaccount.smtp_server, Money_account.accdesc).filter(Landlord.id == id).one_or_none()

    managers = [value for (value,) in Manager.query.with_entities(Manager.name).all()]
    emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    return landlord, managers, emailaccs, bankaccs


def get_landlords():
    landlords = Landlord.query.join(Manager).with_entities(Landlord.id, Landlord.name, Landlord.addr,
                   Landlord.taxdate, Manager.name.label("manager")).all()

    return landlords


def get_loan(id):
    loan = \
        Loan.query.join(Typeadvarr).join(Typefreq).with_entities(Loan.id, Loan.code, Loan.interest_rate,
                 Loan.end_date, Loan.lender, Loan.borrower, Loan.notes, Loan.val_date, Loan.valuation,
                     Loan.interestpa, Typeadvarr.advarrdet, Typefreq.freqdet) \
            .filter(Loan.id == id).one_or_none()

    return loan


def get_loan_options():
    # return options for each multiple choice control in money_edit and money_filter pages
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]

    return advarrdets, freqdets

def getloans():
    loans = \
        Loan.query \
            .with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender, Loan.borrower,
                           Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa)\
            .all()
    loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('totval'),
                        func.sum(Loan.interestpa).label('totint')).filter().first()
    return loans, loansum


def getloanstatement():
    loanstatement = \
        Loan_statement.query \
            .with_entities(Loan_statement.id, Loan_statement.date, Loan_statement.memo,
                           Loan_statement.transaction, Loan_statement.rate, Loan_statement.interest,
                           Loan_statement.add_interest, Loan_statement.balance) \
            .all()
    # if loanstatement is None:
    #     flash('Invalid loan id')
    #     return redirect(url_for('auth.login'))
    return loanstatement


def get_moneyaccount(id):
    if id > 0:
        # existing bank account
        moneyacc = \
            Money_account.query \
                .with_entities(Money_account.id, Money_account.bankname, Money_account.accname, Money_account.sortcode,
                               Money_account.accnum, Money_account.accdesc) \
                .filter(Money_account.id == id) \
                .one_or_none()
        if moneyacc is None:
            flash('Invalid account')
            return redirect(url_for('auth.login'))
    else:
        # new bank account
        moneyacc = {
            'id': 0
        }

    return moneyacc


def get_moneydets():
    moneydets = \
        Money_account.query \
            .with_entities(Money_account.id, Money_account.bankname, Money_account.accname, Money_account.sortcode,
                           Money_account.accnum, Money_account.accdesc,
                           func.mjinn.acc_balance(Money_account.id, 1, date.today()).label('cbalance'),
                           func.mjinn.acc_balance(Money_account.id, 0, date.today()).label('ubalance')) \
            .all()

    accsums = Money_account.query.with_entities(func.mjinn.acc_total(1).label('cleared'),
                                            func.mjinn.acc_total(0).label('uncleared')).filter().first()

    return moneydets, accsums


def get_moneyitem(id):
    bankitem = \
        Money_item.query \
            .join(Money_account) \
            .join(Money_category) \
            .with_entities(Money_item.id, Money_item.num, Money_item.date,
                           Money_item.payer, Money_item.amount, Money_item.memo,
                           Money_account.accdesc, Money_category.cat_name, Money_item.cleared) \
            .filter(Money_item.id == id) \
            .one_or_none()

    return bankitem


def get_moneyitems(id):
    moneyitems = \
        Money_item.query \
            .join(Money_account) \
            .join(Money_category) \
            .with_entities(Money_item.id, Money_item.num, Money_item.date,
                           Money_item.payer, Money_item.amount, Money_item.memo,
                           Money_account.accdesc, Money_category.cat_name, Money_item.cleared) \
            .filter(Money_account.id == id).union\
            (Income.query \
             .join(Money_account) \
             .join(Incomealloc)
             .with_entities(Income.id, literal("0").label('num'), Income.date,
                            Income.payer, Income.amount, Incomealloc.rentcode,
                            Money_account.accdesc, literal("Jinn BACS income").label('cat_name'), literal("1").label('cleared')) \
             .filter(Money_account.id == id)).order_by(desc(Money_item.date), desc(Income.date)) \
                    .limit(200)

    accsums = Money_item.query.with_entities(func.mjinn.acc_balance(id, 1, date.today()) \
                                             .label('cbalance'), func.mjinn.acc_balance(Money_account.id, 0, date.today()).label('ubalance')) \
            .filter().first()

    return moneyitems, accsums


def get_money_options():
    # return options for each multiple choice control in money_edit and money_filter pages
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs.insert(0, "all accounts")
    cats = [value for (value,) in Money_category.query.with_entities(Money_category.cat_name).all()]
    cats.insert(0, "all categories")
    cleareds = ["Cleared", "Uncleared"]

    return bankaccs, cats, cleareds


def getproperty(id):
    if id > 0:
        # existing property
        property = \
        Property.query \
            .join(Typeproperty) \
                .with_entities(Property.id, Property.propaddr, Typeproperty.proptypedet) \
                .filter(Property.id == id) \
                .one_or_none()
        if property is None:
            flash('Invalid property id')
            return redirect('/properties')
    else:
        # new property
        property = {
            'id': 0
        }
    proptypedets = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]
    return property, proptypedets


def get_queryoptions():
    # return options for each multiple choice control in home page and queries page
    actypes = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    actypes.insert(0, "all actypes")
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    landlords.insert(0, "all landlords")
    floads = [value for (value,) in Jstore.query.with_entities(Jstore.name).all()]
    prdeliveries = [value for (value,) in Typeprdelivery.query.with_entities(Typeprdelivery.prdeliverydet).all()]
    salegrades = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]
    salegrades.insert(0, "all salegrades")
    statuses = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    statuses.insert(0, "all statuses")
    tenures = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]
    tenures.insert(0, "all tenures")
    options = ("Include", "Exclude", "Only")

    return actypes, floads, landlords, options, prdeliveries, salegrades, statuses, tenures


def getrental(id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    # all to be shown in rental.html, allowing editing an existing rental (for which info is fetched via Rental.id
    # or creation of a new rent (signified by id==0), in which case we have to "invent" an object with the same
    # attributes as would have been fetched from the database but with "blanks", or default values, as desired for
    # creating a new rental; --- seems like Flask is happy for it not even to have the fields which will be
    # referenced, so just put in any defaults desired)
    if id > 0:
        # existing rental
        rental = \
            Rental.query \
                .join(Typeadvarr) \
                .join(Typefreq) \
                .with_entities(Rental.id, Rental.rentalcode, Rental.arrears, Rental.startrentdate,
                               Rental.astdate, Rental.lastgastest,
                               Rental.note, Rental.propaddr, Rental.rentpa, Rental.tenantname,
                               Typeadvarr.advarrdet, Typefreq.freqdet) \
                .filter(Rental.id == id) \
                .one_or_none()
        if rental is None:
            flash('Invalid rentalcode')
            return redirect(url_for('auth.login'))
    else:
        # new rent
        rental = {
            'id': 0
        }

    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    return rental, advarrdets, freqdets


def getrentals():
    rentals = \
        Rental.query \
            .with_entities(Rental.id, Rental.rentalcode, Rental.propaddr, Rental.tenantname,
                           Rental.startrentdate, Rental.astdate, Rental.lastgastest, Rental.rentpa)\
            .all()
    rentsum = Rental.query.with_entities(func.sum(Rental.rentpa).label('totrent')).filter().first()[0]
    return rentals, rentsum


def getrentalstatem():

    rentalstatem = \
        Rental_statement.query \
            .with_entities(Rental_statement.id, Rental_statement.date, Rental_statement.memo,
                           Rental_statement.amount, Rental_statement.payer, Rental_statement.balance) \
            .all()
    # if rentalstatem is None:
    #     flash('Invalid rental id')
    #     return redirect(url_for('auth.login'))
    return rentalstatem


def get_rentobjects(action, name):
    jname = name
    agentdetails = request.form.get("agentdetails") or ""
    propaddr = request.form.get("propaddr") or ""
    rentcode = request.form.get("rentcode") or ""
    source = request.form.get("source") or ""
    tenantname = request.form.get("tenantname") or ""
    enddate = request.form.get("enddate") or date.today() + relativedelta(days=35)
    runsize = request.form.get("runsize") or 300
    qfilterbasic = getqfilterbasic(action, agentdetails, propaddr, rentcode, source, tenantname)
    if action == "basic" or action == "external":
        rentprops = getrentobjs(action, qfilterbasic, runsize)
        return agentdetails, propaddr, rentcode, source, tenantname, rentprops
    else:
        actypes, floads, landlords, options, prdeliveries, salegrades, statuses, tenures = get_queryoptions()
        if request.method == "POST":
            jname = request.form.get("jname")
            actype = request.form.getlist("actype")
            arrears = request.form.get("arrears")
            landlord = request.form.getlist("landlord")
            prdelivery = request.form.getlist("prdelivery")
            rentpa = request.form.get("rentpa")
            rentperiods = request.form.get("rentperiods")
            salegrade = request.form.getlist("salegrade")
            status = request.form.getlist("status")
            tenure = request.form.getlist("tenure")
        else:
            returns = Jstore.query.with_entities(Jstore.content).filter(Jstore.name == jname)[0][0]
            print(returns)
            returns = json.loads(returns)
            agentdetails = returns["agd"]
            actype = returns["act"]
            arrears = returns["arr"]
            landlord = returns["lld"]
            prdelivery = returns["prd"]
            propaddr = returns["pop"]
            rentcode = returns["rcd"]
            rentpa = returns["rpa"]
            rentperiods = returns["rpd"]
            salegrade = returns["sal"]
            status = returns["sta"]
            source = returns["soc"]
            tenantname = returns["tna"]
            tenure = returns["ten"]
        qfilter = getqfilterbasic(action, agentdetails, propaddr, rentcode, source, tenantname)
        if actype and actype != actypes and actype[0] != "all actypes":
            qfilter.append(Typeactype.actypedet.in_(actype))
        if arrears and arrears != "":
            qfilter.append(text("Rent.arrears {}".format(arrears)))
        if landlord and landlord != landlords and landlord[0] != "all landlords":
            qfilter.append(Landlord.name.in_(landlord))
        if prdelivery and prdelivery != prdeliveries and prdelivery != "":
            qfilter.append(Typeprdelivery.prdeliverydet.in_(prdelivery))
        if rentpa and rentpa != "":
            qfilter.append(text("Rent.rentpa {}".format(rentpa)))
        if rentperiods and rentperiods != "":
            qfilter.append(text("Rent.rentperiods {}".format(rentperiods)))
        if salegrade and salegrade != salegrades and salegrade[0] != "all salegrades":
            qfilter.append(Typesalegrade.salegradedet.in_(salegrade))
        if status and status != statuses and status[0] != "all statuses":
            qfilter.append(Typestatus.statusdet.in_(status))
        if tenure and tenure != tenures and tenure[0] != "all tenures":
            qfilter.append(Typetenure.tenuredet.in_(tenure))
        if action == "save":
            store = {}
            store["act"] = actype
            store["agd"] = agentdetails
            store["arr"] = arrears
            store["lld"] = landlord
            store["prd"] = prdelivery
            store["pop"] = propaddr
            store["rcd"] = rentcode
            store["rpa"] = rentpa
            store["rpd"] = rentperiods
            store["sal"] = salegrade
            store["soc"] = source
            store["sta"] = status
            store["tna"] = tenantname
            store["ten"] = tenure
            j_id = \
                Jstore.query.with_entities(Jstore.id).filter \
                    (Jstore.name == jname).one()[0]
            if j_id:
                jstore = Jstore.query.get(j_id)
                jstore.name = jname
                jstore.content = json.dumps(store)
                db.session.commit()
            else:
                jstore = Jstore()
                jstore.name = jname
                jstore.content = json.dumps(store)
                db.session.add(jstore)
            db.session.commit()
        rentprops = getrentobjs(action, qfilter, runsize)

        return actypes, floads, landlords, options, prdeliveries, salegrades, statuses, tenures, \
               actype, agentdetails, arrears, enddate, jname, landlord, prdelivery, propaddr, rentcode, rentpa, \
               rentperiods, runsize, salegrade, source, status, tenantname, tenure, rentprops


def getqfilterbasic(action, agentdetails, propaddr, rentcode, source, tenantname):
    qfilterbasic = []
    if agentdetails and agentdetails != "":
        if action == "external":
            qfilterbasic.append(Extrent.agentdetails.ilike('%{}%'.format(agentdetails)))
        else:
            qfilterbasic.append(Agent.agdetails.ilike('%{}%'.format(agentdetails)))
    if propaddr and propaddr != "":
        if action == "external":
            qfilterbasic.append(Extrent.propaddr.ilike('%{}%'.format(propaddr)))
        else:
            qfilterbasic.append(Property.propaddr.ilike('%{}%'.format(propaddr)))
    if rentcode and rentcode != "":
        if action == "external":
            qfilterbasic.append(Extrent.rentcode.startswith([rentcode]))
        else:
            qfilterbasic.append(Rent.rentcode.startswith([rentcode]))
    if source and source != "":
        if action == "external":
            qfilterbasic.append(Extrent.source.ilike('%{}%'.format(source)))
        else:
            qfilterbasic.append(Rent.source.ilike('%{}%'.format(source)))
    if tenantname and tenantname != "":
        if action == "external":
            qfilterbasic.append(Extrent.tenantname.ilike('%{}%'.format(tenantname)))
        else:
            qfilterbasic.append(Rent.tenantname.ilike('%{}%'.format(tenantname)))

    return qfilterbasic


def getrentobjs(action, qfilter, runsize):
    if action == "basic":
        rentobjs = \
            Property.query \
                .join(Rent) \
                .outerjoin(Agent) \
                .with_entities(Rent.id, Agent.agdetails, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
                               func.mjinn.next_date(Rent.lastrentdate, Rent.freq_id, 1).label('nextrentdate'),
                               Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname) \
                .filter(*qfilter) \
                .group_by(Rent.id) \
                .limit(runsize).all()
    elif action == "external":
        rentobjs = \
            Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(*qfilter) \
            .limit(runsize).all()
    else:
        rentobjs = \
            Property.query \
                .join(Rent) \
                .join(Landlord) \
                .outerjoin(Agent) \
                .outerjoin(Charge) \
                .join(Typeactype) \
                .join(Typeprdelivery) \
                .join(Typestatus) \
                .join(Typesalegrade) \
                .join(Typetenure) \
                .with_entities(Rent.id, Typeactype.actypedet, Agent.agdetails, Rent.arrears, Rent.lastrentdate,
                               func.mjinn.next_date(Rent.lastrentdate, Rent.freq_id, 1).label('nextrentdate'),
                               Landlord.name, Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname,
                               Typeprdelivery.prdeliverydet, Typesalegrade.salegradedet, Typestatus.statusdet,
                               func.sum(Charge.chargebalance).label('totcharge'),
                               Typetenure.tenuredet) \
                .filter(*qfilter) \
                .group_by(Rent.id) \
                .limit(runsize).all()

    return rentobjs


def getrentobj(id):
    # This method returns "rentobj"; information about a rent, its related property/agent/landlord stuff, plus
    # the list values for various comboboxes, all to be shown in rentobjpage.html, allowing editing an existing
    # rent (for which rent info is fetched via Rent.id or creation of a new rent (signified by id==0), in which
    # case we have to "invent" an object with the same attributes as would have been fetched from the database
    # but with "blanks", or default values, as desired for creating a new rent; --- seems like Flask is happy
    # for it not even to have the fields which will be referenced, so just put in any defaults desired)
    if id > 0:
        # existing rent
        rentobj = \
            Rent.query \
                .join(Landlord) \
                .outerjoin(Agent) \
                .join(Typeactype) \
                .join(Typeadvarr) \
                .join(Typedeed) \
                .join(Typefreq) \
                .join(Typemailto) \
                .join(Typesalegrade) \
                .join(Typestatus) \
                .join(Typetenure) \
                .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                               func.mjinn.next_date(Rent.lastrentdate, Rent.freq_id, 1).label('nextrentdate'),
                               Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname,
                               Agent.agdetails, Landlord.name, Typeactype.actypedet,
                               Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet, Typemailto.mailtodet,
                               Typesalegrade.salegradedet, Typestatus.statusdet,
                               Typetenure.tenuredet) \
                .filter(Rent.id == id) \
                .one_or_none()
        if rentobj is None:
            flash('Invalid rent code')
            return redirect(url_for('auth.login'))
    else:
        # new rent
        rentobj = {
            'id': 0
        }

    actypedets = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    mailtodets = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    salegradedets = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenuredets = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]
    totcharges = Charge.query.join(Rent).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
        filter(Rent.id == id) \
            .one_or_none()[0]
    properties = \
        Property.query \
            .join(Rent) \
            .join(Typeproperty) \
            .with_entities(Property.id, Property.propaddr, Typeproperty.proptypedet) \
            .filter(Rent.id == id) \
            .all()
    return rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, properties, \
           salegradedets, statusdets, tenuredets, totcharges
