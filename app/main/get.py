from flask import flash, redirect, url_for, request
from sqlalchemy import asc, desc, extract, func, literal, and_, or_
from app.models import Agent, Charge, Chargetype, Datef2, Datef4, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Loan, Loan_statement, Manager, Property, Rent, Rental, Rental_statement, Typeactype, Typeadvarr, Typebankacc, Typedeed, \
    Typefreq, Typemailto, Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def filteragents(agd, age, agn):
    agents = \
        Agent.query \
            .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
            .filter(Agent.agdetails.ilike('%{}%'.format(agd)),
                    Agent.agemail.ilike('%{}%'.format(age)),
                    Agent.agnotes.ilike('%{}%'.format(agn))) \
            .all()

    return agents

def filtercharges(rcd, cdt):
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


def filteremailaccs():
    emailaccs = \
        Emailaccount.query \
            .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_user,
                           Emailaccount.smtp_sendfrom, Emailaccount.imap_sentfolder, Emailaccount.imap_draftfolder) \
            .all()
    return emailaccs


def filterextrents():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
    else:
        rcd = "lus"
        ten = ""
        pop = ""
    extrents = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.rentcode.startswith([rcd]),
                    Extrent.tenantname.ilike('%{}%'.format(ten)),
                    Extrent.propaddr.ilike('%{}%'.format(pop))) \
            .all()

    return extrents

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
            .with_entities(Income.id, Income.paydate, Incomealloc.rentcode, Income.total, Income.payer,
                           Typebankacc.accdesc, Chargetype.chargedesc, Typepayment.paytypedet) \
            .filter(Incomealloc.rentcode.startswith([rcd]),
                    Income.payer.ilike('%{}%'.format(pay)),
                    Chargetype.chargedesc.ilike('%{}%'.format(typ))) \
            .limit(50).all()
    return income


def filterlandlords():
    landlords = \
        Landlord.query.join(Manager) \
            .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate,
                           Manager.name.label("manager")) \
            .all()
    return landlords


def filterrentobjs(rcd, ten, pop):
    rentobjs = \
        Property.query \
            .join(Rent) \
            .join(Landlord) \
            .outerjoin(Agent) \
            .with_entities(Rent.id, Rent.rentcode, Rent.tenantname, Rent.rentpa, Rent.arrears, Rent.lastrentdate,
                           Property.propaddr, Landlord.name, Agent.agdetails) \
            .filter(Rent.rentcode.startswith([rcd]),
                    Rent.tenantname.ilike('%{}%'.format(ten)),
                    Property.propaddr.ilike('%{}%'.format(pop))) \
            .all()
    return rentobjs


def getagent(id):
    ida = id
    agent = \
        Agent.query \
            .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
            .filter(Agent.id == ida) \
            .one_or_none()
    if agent is None:
        flash('Invalid agent code')
        return redirect(url_for('main.agents'))
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


def getextrent(id):
    # if request.method == "POST":
    #
    #     return redirect(url_for('main.index'))
    # else:
    # pass
    extrent = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.id == id) \
                .one_or_none()
    if extrent is None:
        flash('N')
        return redirect(url_for('main.index'))
    return extrent


def getincome(id):
    if id > 0:
        # existing income
        income = \
            Income.query.join(Typebankacc) \
                .join(Typepayment) \
                .with_entities(Income.id, Income.paydate, Income.total, Income.payer,
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
                .with_entities(Loan.id, Loan.code, Loan.start_intrate, Loan.end_date,
                               Loan.lender, Loan.borrower, Loan.notes, Loan.val_date, Loan.valuation,
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
            .with_entities(Loan.id, Loan.code, Loan.start_intrate, Loan.end_date,
                               Loan.lender, Loan.borrower, Loan.notes, Loan.val_date, Loan.valuation)\
            .all()
    loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('totval')).filter().first()[0]
    return loans, loansum


def getloanstatement():

    loanstatement = \
        Loan_statement.query \
            .with_entities(Loan_statement.id, Loan_statement.date, Loan_statement.memo,
                           Loan_statement.transaction, Loan_statement.rate, Loan_statement.interest, \
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


def getrental(id):
    # This method returns a "rental" object
    # information about a rental
    # plus all the list values to offer for various comboboxes
    # all of this is to be shown in rentalpage.html
    # that allows either editing etc. of an existing rental (whose `id` is specified)
    # (in which case we fetch the rent info to edit)
    # or it allows creation of a new rental (signified by id==0)
    # (in which case for the rental info we have to "invent" an object
    # with the same attributes as would have been fetched from the database
    # but with "blanks", or default values, as desired for creating a new rental
    # --- seems like Flask is happy for it not even to have the fields which will be referenced
    # so just put in any defaults desired)
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


def getrentobj(id):
    # This method returns a "rentobj" object
    # information about a rent, plus its related property/agent/landlord stuff
    # plus all the list values to offer for various comboboxes
    # all of this is to be shown in rentobjpage.html
    # that allows either editing etc. of an existing rent (whose `id` is specified)
    # (in which case we fetch the rent info to edit)
    # or it allows creation of a new rent (signified by id==0)
    # (in which case for the rent info we have to "invent" an object
    # with the same attributes as would have been fetched from the database
    # but with "blanks", or default values, as desired for creating a new rent
    # --- seems like Flask is happy for it not even to have the fields which will be referenced
    # so just put in any defaults desired)
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
