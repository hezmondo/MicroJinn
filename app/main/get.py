import json
from app import db
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import flash, redirect, url_for, request
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app.models import Agent, Charge, Chargetype, Date_f2, Date_f4, Extmanager, Extrent, Income, Incomealloc, \
    Jstore, Landlord, Loan, Loan_statement, Manager, Money_category, Money_transaction, \
    Property, Rent, Rental, Rental_statement, Typeactype, \
    Typeadvarr, Typebankacc, Typedeed, Typefreq, Typemailto, Typepayment, Typeprdelivery, Typeproperty, \
    Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def filteragents(agd, age, agn):
    agents = \
        Agent.query \
            .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
            .filter(Agent.agdetails.ilike('%{}%'.format(agd)),
                    Agent.agemail.ilike('%{}%'.format(age)),
                    Agent.agnotes.ilike('%{}%'.format(agn))) \
            .all()

    return agents

def filteremailaccs():
    emailaccs = \
        Emailaccount.query \
            .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_user,
                           Emailaccount.smtp_sendfrom, Emailaccount.imap_sentfolder, Emailaccount.imap_draftfolder) \
            .all()
    return emailaccs


def filterheadrents():
#     if request.method == "POST":
        # hrcd = request.form["headrentcode"]
        # agd = request.form["agentdetails"]
        # pop = request.form["propaddr"]
    # else:
        # headrents = getheadrents("", "COMP", "")
    headrents = None
    return headrents


def filterincome(rcd, pay, typ):
    income = \
        Incomealloc.query.join(Income) \
            .join(Chargetype) \
            .join(Typebankacc) \
            .join(Typepayment) \
            .with_entities(Income.id, Income.date, Incomealloc.rentcode, Income.amount, Income.payer,
                           Typebankacc.accdesc, Chargetype.chargedesc, Typepayment.paytypedet) \
            .filter(Incomealloc.rentcode.startswith([rcd]),
                    Income.payer.ilike('%{}%'.format(pay)),
                    Chargetype.chargedesc.ilike('%{}%'.format(typ))) \
            .limit(50).all()

    return income


def getaccount(id):
    if id > 0:
        # existing account
        account = \
            Typebankacc.query \
                .with_entities(Typebankacc.id, Typebankacc.bankname, Typebankacc.accname, Typebankacc.sortcode,
                               Typebankacc.accnum, Typebankacc.accdesc) \
                .filter(Typebankacc.id == id) \
                .one_or_none()
        if account is None:
            flash('Invalid account')
            return redirect(url_for('auth.login'))
    else:
        # new account
        account = {
            'id': 0
        }

    return account


def getaccounts():
    accounts = \
        Typebankacc.query \
            .with_entities(Typebankacc.id, Typebankacc.bankname, Typebankacc.accname, Typebankacc.sortcode,
                           Typebankacc.accnum, Typebankacc.accdesc,
                           func.mjinn.acc_balance(Typebankacc.id, 1, date.today()).label('cbalance'),
                           func.mjinn.acc_balance(Typebankacc.id, 0, date.today()).label('ubalance')) \
            .all()

    accsums = Typebankacc.query.with_entities(func.mjinn.acc_total(1).label('cleared'),
                        func.mjinn.acc_total(0).label('uncleared')).filter().first()

    return accounts, accsums


def get_acctrans(id):
    acctrans = \
        Money_transaction.query \
            .join(Typebankacc) \
            .join(Money_category) \
            .with_entities(Money_transaction.id, Money_transaction.num, Money_transaction.date,
                           Money_transaction.payer, Money_transaction.amount, Money_transaction.memo,
                           Typebankacc.accdesc, Money_category.cat_name, Money_transaction.cleared) \
            .filter(Typebankacc.id == id) \
            .order_by(desc(Money_transaction.date)).limit(100).all()

    accsums = Money_transaction.query.with_entities(func.mjinn.acc_balance(Typebankacc.id, 1,
                       date.today()).label('cbalance'), func.mjinn.acc_balance(Typebankacc.id,
                               0, date.today()).label('ubalance')) \
            .filter().first()
    accs = [value for (value,) in Typebankacc.query.with_entities(Typebankacc.accdesc).all()]
    accs.insert(0, "all accounts")
    cats = [value for (value,) in Money_category.query.with_entities(Money_category.cat_name).all()]
    cats.insert(0, "all categories")
    cleareds = ["Cleared", "Uncleared"]

    return acctrans, accs, accsums, cats, cleareds


def getagent(id):
    if id > 0:
        # existing agent
        agent = \
            Agent.query \
                .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
                .filter(Agent.id == id) \
                .one_or_none()
        if agent is None:
            flash('Invalid agent code')
            return redirect(url_for('main.agents'))
    else:
        # new agent
        agent = {
            'id': 0
        }
    return agent


def getcharge(id):
    charge = \
        Charge.query \
            .join(Rent) \
            .join(Chargetype) \
            .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                           Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(Charge.id == id) \
            .one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
    return charge, chargedescs


def get_charges(rcd, cdt):
    charges = \
        Charge.query \
            .join(Rent) \
            .join(Chargetype) \
            .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                           Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(Rent.rentcode.startswith([rcd]),
                    Charge.chargedetails.ilike('%{}%'.format(cdt))) \
            .all()

    return charges


def getemailacc(id):
    if id > 0:
        # existing emailacc
        emailacc = \
            Emailaccount.query \
                .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_port,
                               Emailaccount.smtp_timeout, Emailaccount.smtp_debug, Emailaccount.smtp_tls,
                               Emailaccount.smtp_user, Emailaccount.smtp_password, Emailaccount.smtp_sendfrom,
                               Emailaccount.imap_server, Emailaccount.imap_port, Emailaccount.imap_tls,
                               Emailaccount.imap_user, Emailaccount.imap_password, Emailaccount.imap_sentfolder,
                               Emailaccount.imap_draftfolder) \
                .filter(Emailaccount.id == id) \
                .one_or_none()
    else:
        # new emailacc
        emailacc = {
            'id': 0
        }
    return emailacc


def getexternalrent(id):
    # if request.method == "POST":
    #
    #     return redirect(url_for('main.index'))
    # else:
    # pass
    externalrent = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.id == id) \
                .one_or_none()
    if externalrent is None:
        flash('N')
        return redirect(url_for('main.index'))
    return externalrent


def getincome(id):
    if id > 0:
        # existing income
        income = \
            Income.query.join(Typebankacc) \
                .join(Typepayment) \
                .with_entities(Income.id, Income.date, Income.amount, Income.payer,
                               Typepayment.paytypedet, Typebankacc.accdesc) \
                .filter(Income.id == id) \
                .one_or_none()
        if income is None:
            flash('Invalid income id')
            return redirect('/income')
        incomeallocs = \
            Incomealloc.query.join(Landlord) \
                .join(Chargetype) \
                .with_entities(Incomealloc.id, Incomealloc.income_id, Incomealloc.alloc_id, Incomealloc.rentcode,
                               Incomealloc.total, Landlord.name, Chargetype.chargedesc) \
                .filter(Incomealloc.income_id == id) \
                .all()
    else:
        # new income
        income = {
            'id': 0,
            'paydate': "2019-09-01"
        }
        incomeallocs = {
            'id': 0
        }
    bankaccs = [value for (value,) in Typebankacc.query.with_entities(Typebankacc.accdesc).all()]
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    paytypedets = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]

    return bankaccs, chargedescs, income, incomeallocs, landlords, paytypedets


def getlandlord(id):
    if id > 0:
        # existing landlord
        landlord = \
            Landlord.query.join(Manager).join(Emailaccount).join(Typebankacc) \
                .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate,
                               Manager.name.label("manager"), Emailaccount.smtp_server, Typebankacc.accdesc) \
                .filter(Landlord.id == id) \
                .one_or_none()
        if landlord is None:
            flash('Invalid landlord id')
            return redirect('/landlords')
    else:
        # new landlord
        landlord = {
            'id': 0,
            'taxdate': "2000-04-05"
        }
    managers = [value for (value,) in Manager.query.with_entities(Manager.name).all()]
    emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
    bankaccs = [value for (value,) in Typebankacc.query.with_entities(Typebankacc.accdesc).all()]
    return landlord, managers, emailaccs, bankaccs


def getlandlords():
    landlords = \
        Landlord.query.join(Manager) \
            .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate,
                           Manager.name.label("manager")) \
            .all()

    return landlords


def getloan(id):
    # This method returns a "loan" object
    # information about a loan
    # plus all the list values to offer for various comboboxes
    # all of this is to be shown in loanpage.html
    # that allows either editing etc. of an existing loan (whose `id` is specified)
    # (in which case we fetch the rent info to edit)
    # or it allows creation of a new loan (signified by id==0)
    # (in which case for the loan info we have to "invent" an object
    # with the same attributes as would have been fetched from the database
    # but with "blanks", or default values, as desired for creating a new loan
    # --- seems like Flask is happy for it not even to have the fields which will be referenced
    # so just put in any defaults desired)
    if id > 0:
        # existing loan
        loan = \
            Loan.query \
                .join(Typeadvarr) \
                .join(Typefreq) \
                .with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender, Loan.borrower,
                               Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa,
                               Typeadvarr.advarrdet, Typefreq.freqdet) \
                .filter(Loan.id == id) \
                .one_or_none()
        if loan is None:
            flash('Invalid loancode')
            return redirect(url_for('auth.login'))
    else:
        # new rent
        loan = {
            'id': 0
        }

    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    return loan, advarrdets, freqdets


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


def getqueryoptions():
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

    return actypes, floads, landlords, salegrades, statuses, tenures, options, prdeliveries


def getrental(id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    # all to be shown in rentalpage.html, allowing editing an existing rental (for which info is fetched via Rental.id
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


def getrentalstatement():

    rentalstatement = \
        Rental_statement.query \
            .with_entities(Rental_statement.id, Rental_statement.date, Rental_statement.memo,
                           Rental_statement.amount, Rental_statement.payer, Rental_statement.balance) \
            .all()
    # if rentalstatement is None:
    #     flash('Invalid rental id')
    #     return redirect(url_for('auth.login'))
    return rentalstatement


def getrentobjects(action, name):
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
        actypes, floads, landlords, salegrades, statuses, tenures, options, prdeliveries = getqueryoptions()
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
