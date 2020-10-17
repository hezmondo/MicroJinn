import json
import sqlalchemy
from app import db
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import flash, redirect, url_for, request, session
from flask_login import current_user, login_required
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app.main.functions import commit_to_database
from app.models import Agent, Charge, Chargetype, Docfile, Extmanager, Extrent, Formletter, Headrent, Income, \
    Incomealloc, Jstore, Landlord, Lease, Lease_uplift_type, \
    Loan, Loan_statement, Manager, Money_category, \
    Money_item, Property, Rent, Rental, Rental_statement, Typeactype, \
    Typeadvarr, Money_account, Template, Typedeed, Typefreq, Typedoc, Typemailto, Typepayment, Typeprdelivery, \
    Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


# agents
def get_agents():
    if request.method == "POST":
        agd = request.form.get("address") or ""
        age = request.form.get("email") or ""
        agn = request.form.get("notes") or ""
        agents = Agent.query.filter(Agent.agdetails.ilike('%{}%'.format(agd)), Agent.agemail.ilike('%{}%'.format(age)),
                        Agent.agnotes.ilike('%{}%'.format(agn))).all()
    else:
        id_list = get_idlist_recent("recent_agents")
        agents = Agent.query.filter(Agent.id.in_(id_list))
    return agents


def get_agent(id):
    pop_idlist_recent("recent_agents", id)
    agent = Agent.query.filter(Agent.id == id).one_or_none()

    return agent


# charges
def get_charges(rentid):
    qfilter = []
    if rentid == "":
        rcd = request.form.get("rentcode") or ""
        cdt = request.form.get("chargedetails") or ""
        qfilter.append(Rent.rentcode.startswith([rcd]))
        qfilter.append(Charge.chargedetails.ilike('%{}%'.format(cdt)))
    else:
        qfilter.append(Charge.rent_id == rentid)

    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                     Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(*qfilter).all()

    return charges


def get_charge(id):
    charge = \
        Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
               Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
                .filter(Charge.id == id).one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]

    return charge, chargedescs


# docfiles
def get_docfile(id, action):
    if action == "new":
        # new docfile has to be attached to an existing rent, so incoming id in this case is rent id:
        rentcode = Rent.query.with_entities(Rent.rentcode).filter(Rent.id == id).one()[0]
        docfile = {
            'id': 0,
            'rentid': id,
            'rentcode': rentcode,
            'desc': "Letter",
            'summary': "letter in",
            'out_in': 0
        }
        dfoutin = "in"
    else:
        # existing docfile, so incoming id is docfile id:
        docfile = Docfile.query.join(Rent).join(Typedoc).with_entities(Docfile.id, Docfile.summary, Docfile.out_in,
                       Docfile.docfile_text, Docfile.docfile_date, Rent.rentcode, Rent.id.label("rentid"),
                                                                       Typedoc.desc) \
                    .filter(Docfile.id == id).one_or_none()
        # messy - must be better solution:
        dfoutin = "out" if docfile.out_in == 1 else 0

    return docfile, dfoutin


def get_docfiles(rentid):
    docfile_filter = []
    dfoutin = "all"
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        dfsum = request.form.get("summary") or ""
        dftx = request.form.get("docfile_text") or ""
        dfty = request.form.get("doc_type") or ""
        dfoutin = request.form.get("out_in") or ""
        if rcd and rcd != "":
            docfile_filter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
        if dfsum and dfsum != "":
            docfile_filter.append(Docfile.summary.ilike('%{}%'.format(dfsum)))
        if dftx and dftx != "":
            docfile_filter.append(Docfile.docfile_text.ilike('%{}%'.format(dftx)))
        if dfty and dfty != "":
            docfile_filter.append(Typedoc.desc.ilike('%{}%'.format(dfty)))
        if dfoutin == "out":
            docfile_filter.append(Docfile.out_in == 1)
        elif dfoutin == "in":
            docfile_filter.append(Docfile.out_in == 0)
    if rentid > 0:
        docfile_filter.append(Docfile.rent_id == rentid)

    docfiles = Docfile.query.join(Rent).join(Typedoc).with_entities(Docfile.id, Docfile.docfile_date,
                Docfile.summary, Docfile.docfile_text, Typedoc.desc, Docfile.out_in, Rent.rentcode) \
        .filter(*docfile_filter).all()

    return docfiles, dfoutin

# email accounts
def get_emailaccounts():
    emailaccs = Emailaccount.query.all()

    return emailaccs


def get_emailaccount(id):
    emailacc = Emailaccount.query.filter(Emailaccount.id == id).one_or_none()

    return emailacc


# external rents
def get_externalrent(id):
    externalrent = Extrent.query.join(Extmanager).with_entities(Extrent.rentcode, Extrent.propaddr,
                    Extrent.tenantname, Extrent.owner, Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate,
                        Extrent.source, Extrent.status, Extmanager.codename, Extrent.agentdetails) \
        .filter(Extrent.id == id).one_or_none()

    return externalrent


# formletters
def get_formletter(id):

    formletter = Formletter.query.join(Typedoc).join(Template).with_entities(Formletter.id, Formletter.code,
                                 Formletter.summary, Formletter.subject, Formletter.block, Formletter.bold,
                                 Typedoc.desc, Template.desc.label("template")) \
           .filter(Formletter.id == id).one_or_none()

    return formletter


def get_formletters(action):
    if request.method == "POST":
        code = request.form.get("code") or ""
        summary = request.form.get("summary") or ""
        subject = request.form.get("subject") or ""
        part1 = request.form.get("part1") or ""
        block = request.form.get("block") or ""
        formletters = Formletter.query.filter(Formletter.code.ilike('%{}%'.format(code)),
                               Formletter.subject.ilike('%{}%'.format(summary)),
                               Formletter.subject.ilike('%{}%'.format(subject)),
                               Formletter.part1.ilike('%{}%'.format(part1)),
                                       Formletter.block.ilike('%{}%'.format(block))).all()
    elif action == "lease":
        formletters = Formletter.query.filter(Formletter.code.ilike('LEQ-%'))
    else:
        id_list = json.loads(current_user.recent_formletters)
        formletters = Formletter.query.filter(Formletter.id.in_(id_list))

    return formletters


# head rents
def get_headrents():
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    statusdets.insert(0, "all statuses")
    headrents = Headrent.query.join(Typestatus).outerjoin(Agent).with_entities(Agent.agdetails, Headrent.id,
                Headrent.hrcode, Headrent.rentpa, Headrent.arrears, Headrent.freq_id, Headrent.lastrentdate,
                Headrent.propaddr,
                func.mjinn.next_date(Headrent.lastrentdate, Headrent.freq_id, 1).label('nextrentdate'),
                Typestatus.statusdet).limit(100).all()
    return headrents, statusdets


def get_headrent(id):
    headrent = \
        Headrent.query \
            .join(Landlord) \
            .outerjoin(Agent) \
            .join(Typeadvarr) \
            .join(Typefreq) \
            .join(Typestatus) \
            .join(Typetenure) \
            .with_entities(Headrent.id, Headrent.hrcode, Headrent.arrears, Headrent.datecode, Headrent.lastrentdate,
                           Headrent.propaddr, Headrent.rentpa, Headrent.reference, Headrent.note, Headrent.source,
                           Landlord.landlordname, Agent.agdetails, Typeadvarr.advarrdet, Typefreq.freqdet,
                           Typestatus.statusdet, Typetenure.tenuredet,
        # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
            func.mjinn.next_rent_date(Headrent.id, 2, 1).label('nextrentdate')) \
        .filter(Headrent.id == id) \
            .one_or_none()

    return headrent

# income
def get_incomeitems():
    qfilter = []
    payer = request.form.get("payer") or ""
    if payer and payer != "":
        qfilter.append(Income.payer.ilike('%{}%'.format(payer)))
    rentcode = request.form.get("rentcode") or ""
    if rentcode and rentcode != "":
        qfilter.append(Incomealloc.rentcode.startswith([rentcode]))
    accountdesc = request.form.get("accountdesc") if request.method == "POST" else ""
    paymtype = request.form["paymtype"] if request.method == "POST" else ""
    if accountdesc and accountdesc != "" and accountdesc != "all accounts":
        qfilter.append(Money_account.accdesc == accountdesc)
    if paymtype and paymtype != ""and paymtype != "all payment types":
        qfilter.append(Typepayment.paytypedet == paymtype)

    incomeitems = Incomealloc.query.join(Income).join(Chargetype).join(Money_account).join(Typepayment) \
            .with_entities(Income.id, Income.date, Incomealloc.rentcode, Income.amount, Income.payer,
                           Money_account.accdesc, Chargetype.chargedesc, Typepayment.paytypedet) \
            .filter(*qfilter).order_by(desc(Income.date)).limit(50).all()

    return incomeitems


def get_incomeoptions():
    # return options for multiple choice controls in income
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    bankaccs.insert(0, "all accounts")
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]
    paytypes.insert(0, "all payment types")

    return bankaccs, paytypes


def get_incomeobject(id):
    income = Income.query.join(Money_account).join(Typepayment).with_entities(Income.id, Income.date, Income.amount,
              Income.payer, Typepayment.paytypedet, Money_account.accdesc).filter(Income.id == id).one_or_none()

    incomeallocs = Incomealloc.query.join(Chargetype).join(Rent).with_entities(Incomealloc.id,
                    Incomealloc.income_id, Rent.rentcode, Incomealloc.amount.label("alloctot"),
                    Chargetype.chargedesc).filter(Incomealloc.income_id == id).all()

    return income, incomeallocs


def get_incomeobjectoptions():
    # return options for multiple choice controls in income_object
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    paytypes = [value for (value,) in Typepayment.query.with_entities(Typepayment.paytypedet).all()]

    return bankaccs, chargedescs, landlords, paytypes


def get_incomepost(id):
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


# landlords
def get_landlords():
    landlords = Landlord.query.join(Manager).with_entities(Landlord.id, Landlord.landlordname, Landlord.landlordaddr,
                   Landlord.taxdate, Manager.managername).all()

    return landlords


def get_landlord(id):
    landlord = Landlord.query.join(Manager).join(Emailaccount).join(Money_account).with_entities(Landlord.id,
                 Landlord.landlordname, Landlord.landlordaddr, Landlord.taxdate, Manager.managername,
                     Emailaccount.smtp_server, Money_account.accdesc).filter(Landlord.id == id).one_or_none()

    managers = [value for (value,) in Manager.query.with_entities(Manager.managername).all()]
    emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]

    return landlord, managers, emailaccs, bankaccs


# leases
def get_lease(id, action):
    if action == "new":
        # new lease has to be attached to an existing rent, so incoming id in this case is rent id:
        lease = {
            'id': 0,
            'rent_id': id
        }
    else:
        lease_filter = []
        if action == "rentview":
            # function is being called from rentobject page, so incoming id in this case is rent id:
            lease_filter.append(Rent.id == id)
        else:
            # existing lease, so incoming id is lease id:
            lease_filter.append(Lease.id == id)
        lease = \
            Lease.query.join(Rent).join(Lease_uplift_type).with_entities(Lease.id, Rent.rentcode, Lease.term,
                 Lease.startdate, Lease.startrent, Lease.info, Lease.upliftdate, Lease_uplift_type.uplift_type,
                 Lease.last_value_date, Lease.lastvalue, Lease.impvaluek, Lease.rent_id, Lease.rentcap) \
                .filter(*lease_filter).one_or_none()

    uplift_types = [value for (value,) in Lease_uplift_type.query.with_entities(Lease_uplift_type.uplift_type).all()]

    return lease, uplift_types


def get_leasedata(rent_id, fh_rate, gr_rate, new_gr_a, new_gr_b, yp_low, yp_high):
    resultproxy = db.session.execute(sqlalchemy.text("CALL lex_valuation(:a, :b, :c, :d, :e, :f, :g)"), params={"a": rent_id, "b": fh_rate, "c": gr_rate, "d": new_gr_a, "e": new_gr_b, "f": yp_low, "g": yp_high})
    leasedata = [{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy][0]
    db.session.commit()

    return leasedata


def get_leases():
    lease_filter = []
    rcd = request.form.get("rentcode") or "all rentcodes"
    uld = request.form.get("upliftdays") or "all uplift dates"
    ult = request.form.get("uplift_type") or "all uplift types"
    if rcd and rcd != "all rentcodes":
        lease_filter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
    if uld and uld != "all uplift dates":
        enddate = date.today() + relativedelta(days='{}'.format(uld))
        lease_filter.append(Lease.upliftdate <= enddate)
    if ult and ult != "" and ult != "all uplift types":
        lease_filter.append(Lease_uplift_type.uplift_type.ilike('%{}%'.format(ult)) )

    leases = Lease.query.join(Rent).join(Lease_uplift_type).with_entities(Rent.rentcode, Lease.id, Lease.info,
              func.mjinn.lex_unexpired(Lease.id).label('unexpired'),
              Lease.term, Lease.upliftdate, Lease_uplift_type.uplift_type) \
        .filter(*lease_filter).limit(60).all()

    uplift_types = [value for (value,) in Lease_uplift_type.query.with_entities(Lease_uplift_type.uplift_type).all()]
    uplift_types.insert(0, "all uplift types")

    return leases, uplift_types, rcd, uld, ult


# loans
def get_loan(id):
    loan = \
        Loan.query.join(Typeadvarr).join(Typefreq).with_entities(Loan.id, Loan.code, Loan.interest_rate,
                 Loan.end_date, Loan.lender, Loan.borrower, Loan.notes, Loan.val_date, Loan.valuation,
                     Loan.interestpa, Typeadvarr.advarrdet, Typefreq.freqdet) \
            .filter(Loan.id == id).one_or_none()

    return loan


def get_loan_options():
    # return options for each multiple choice control in loan page
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]

    return advarrdets, freqdets

def get_loans():
    loans = Loan.query.with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender, Loan.borrower,
                           Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa).all()
    loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('totval'),
                        func.sum(Loan.interestpa).label('totint')).filter().first()

    return loans, loansum


def get_loanstatement():
    loanstatement = Loan_statement.query.with_entities(Loan_statement.id, Loan_statement.date, Loan_statement.memo,
                           Loan_statement.transaction, Loan_statement.rate, Loan_statement.interest,
                           Loan_statement.add_interest, Loan_statement.balance).all()

    return loanstatement


# mail
def getmaildata(rent_id, income_id):
    if income_id == 0:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                        Income.date.label("paydate"), Income.amount.label("payamount"), Typepayment.paytypedet) \
                        .filter(Incomealloc.rent_id == rent_id).order_by(desc(Income.date)).limit(1).one_or_none()
        # income_id = incomedata.id
    else:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                        Income.date.label("paydate"), Income.amount.label("payamount"), Typepayment.paytypedet) \
                        .filter(Income.id == income_id).first()
    # allocdata = Incomealloc.join(Chargetype).with_entities(Incomealloc.id, Incomealloc.income_id,
    #                     Incomealloc.rentcode, Incomealloc.amount.label("alloctot"),
    #                     Chargetype.chargedesc).filter(Incomealloc.income_id == income_id).all()
    allocdata = None
    bankdata = Money_account.query.join(Landlord).join(Rent).with_entities(Money_account.accname, Money_account.accnum,
                        Money_account.sortcode, Money_account.bankname).filter(Rent.id == rent_id)\
                .one_or_none()
    addressdata = Landlord.query.join(Rent).join(Manager).with_entities(
                    Landlord.landlordaddr, Manager.manageraddr, Manager.manageraddr2,
                    ).filter(Rent.id == rent_id).one_or_none()

    return incomedata, allocdata, bankdata, addressdata


# money
def get_moneyaccount(id):
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


def get_moneyitems(id, action):
    money_filter = []
    income_filter = []
    values = {'accdesc': 'all accounts', 'payee': 'all', 'memo': 'all', 'category': 'all categories', 'cleared': 'all'}
    if action == "account":
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


# properties
def get_property(id):
    property = Property.query.join(Typeproperty).with_entities(Property.id, Property.propaddr,
                   Typeproperty.proptypedet).filter(Property.id == id).one_or_none()
    proptypedets = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]

    return property, proptypedets


# rentals
def get_rental(id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    rental = Rental.query.join(Typeadvarr).join(Typefreq).with_entities(Rental.id, Rental.rentalcode, Rental.arrears,
                Rental.startrentdate, Rental.astdate, Rental.lastgastest, Rental.note, Rental.propaddr, Rental.rentpa,
                    Rental.tenantname, Typeadvarr.advarrdet, Typefreq.freqdet).filter(Rental.id == id).one_or_none()
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    return rental, advarrdets, freqdets


def getrentals():
    rentals = Rental.query.all()
    rentsum = Rental.query.with_entities(func.sum(Rental.rentpa).label('totrent')).filter().first()[0]

    return rentals, rentsum


def get_rentalstatement():
    rentalstatem = Rental_statement.query.all()

    return rentalstatem


# rent object and associated queries
def get_rentobjects_basic(action):
    qfilterbasic = []
    if action == "view":
        id_list = get_idlist_recent("recent_rents")
        qfilterbasic.append(Rent.id.in_(id_list))
    agentdetails = request.form.get("agentdetails") or ""
    propaddr = request.form.get("propaddr") or ""
    rentcode = request.form.get("rentcode") or ""
    source = request.form.get("source") or ""
    tenantname = request.form.get("tenantname") or ""
    runsize = request.form.get("runsize") or 100
    if action == "external":
        if agentdetails and agentdetails != "":
            qfilterbasic.append(Extrent.agentdetails.ilike('%{}%'.format(agentdetails)))
        if propaddr and propaddr != "":
            qfilterbasic.append(Extrent.propaddr.ilike('%{}%'.format(propaddr)))
        if rentcode and rentcode != "":
            qfilterbasic.append(Extrent.rentcode.startswith([rentcode]))
        if source and source != "":
            qfilterbasic.append(Extrent.source.ilike('%{}%'.format(source)))
        if tenantname and tenantname != "":
            qfilterbasic.append(Extrent.tenantname.ilike('%{}%'.format(tenantname)))
        rentprops = getrentobjs_external(qfilterbasic, runsize)
    else:
        if agentdetails and agentdetails != "":
            qfilterbasic.append(Agent.agdetails.ilike('%{}%'.format(agentdetails)))
        if propaddr and propaddr != "":
            qfilterbasic.append(Property.propaddr.ilike('%{}%'.format(propaddr)))
        if rentcode and rentcode != "":
            qfilterbasic.append(Rent.rentcode.startswith([rentcode]))
        if source and source != "":
            qfilterbasic.append(Rent.source.ilike('%{}%'.format(source)))
        if tenantname and tenantname != "":
            qfilterbasic.append(Rent.tenantname.ilike('%{}%'.format(tenantname)))
        rentprops = getrentobjs_basic(qfilterbasic, runsize)

    return agentdetails, propaddr, rentcode, source, tenantname, rentprops


def get_rentobjects_advanced(action, name):
    jname = name
    agentdetails = request.form.get("agentdetails") or ""
    propaddr = request.form.get("propaddr") or ""
    rentcode = request.form.get("rentcode") or ""
    source = request.form.get("source") or ""
    tenantname = request.form.get("tenantname") or ""
    enddate = request.form.get("enddate") or date.today() + relativedelta(days=35)
    runsize = request.form.get("runsize") or 100
    qfilter = []
    if agentdetails and agentdetails != "":
        qfilter.append(Agent.agdetails.ilike('%{}%'.format(agentdetails)))
    if propaddr and propaddr != "":
        qfilter.append(Property.propaddr.ilike('%{}%'.format(propaddr)))
    if rentcode and rentcode != "":
        qfilter.append(Rent.rentcode.startswith([rentcode]))
    if source and source != "":
        qfilter.append(Rent.source.ilike('%{}%'.format(source)))
    if tenantname and tenantname != "":
        qfilter.append(Rent.tenantname.ilike('%{}%'.format(tenantname)))
    landlords, statusdets, tenuredets = get_queryoptions_common()
    actypedets, floads, options, prdeliveries, salegradedets = get_queryoptions_advanced()
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
    if actype and actype != actypedets and actype[0] != "all actypes":
        qfilter.append(Typeactype.actypedet.in_(actype))
    if arrears and arrears != "":
        qfilter.append(text("Rent.arrears {}".format(arrears)))
    if landlord and landlord != landlords and landlord[0] != "all landlords":
        qfilter.append(Landlord.landlordname.in_(landlord))
    if prdelivery and prdelivery != prdeliveries and prdelivery != "":
        qfilter.append(Typeprdelivery.prdeliverydet.in_(prdelivery))
    if rentpa and rentpa != "":
        qfilter.append(text("Rent.rentpa {}".format(rentpa)))
    if rentperiods and rentperiods != "":
        qfilter.append(text("Rent.rentperiods {}".format(rentperiods)))
    if salegrade and salegrade != salegradedets and salegrade[0] != "all salegrades":
        qfilter.append(Typesalegrade.salegradedet.in_(salegrade))
    if status and status != statusdets and status[0] != "all statuses":
        qfilter.append(Typestatus.statusdet.in_(status))
    if tenure and tenure != tenuredets and tenure[0] != "all tenures":
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
    rentprops = getrentobjs_advanced(qfilter, runsize)

    return actype, agentdetails, arrears, enddate, jname, landlord, prdelivery, propaddr, rentcode, rentpa, \
           rentperiods, runsize, salegrade, source, status, tenantname, tenure, rentprops

def getrentobjs_basic(qfilter, runsize):
    rentobjs = \
        Property.query \
            .join(Rent) \
            .outerjoin(Agent) \
            .with_entities(Rent.id, Agent.agdetails, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname) \
            .filter(*qfilter) \
            .limit(runsize).all()

    return rentobjs


def getrentobjs_external(qfilter, runsize):
    rentobjs = \
        Extrent.query \
        .join(Extmanager) \
        .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                       Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                       Extmanager.codename, Extrent.agentdetails) \
        .filter(*qfilter) \
        .limit(runsize).all()

    return rentobjs


def getrentobjs_advanced(qfilter, runsize):
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
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           Landlord.landlordname, Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname,
                           Typeprdelivery.prdeliverydet, Typesalegrade.salegradedet, Typestatus.statusdet,
                           Typetenure.tenuredet) \
            .filter(*qfilter) \
            .limit(runsize).all()

    return rentobjs


def getrentobj_main(id):
    pop_idlist_recent("recent_rents", id)
    rentobj = \
        Rent.query \
            .join(Landlord) \
            .join(Manager) \
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
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.paid_to_date(Rent.id).label('paidtodate'),
                           func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname,
                           Agent.agdetails, Landlord.landlordname, Manager.managername,
                           Typeactype.actypedet, Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet,
                           Typemailto.mailtodet, Typesalegrade.salegradedet, Typestatus.statusdet,
                           Typetenure.tenuredet) \
            .filter(Rent.id == id) \
            .one_or_none()
    if rentobj is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    properties = \
        Property.query \
            .join(Rent) \
            .join(Typeproperty) \
            .with_entities(Property.id, Property.propaddr, Typeproperty.proptypedet) \
            .filter(Rent.id == id) \
            .all()

    return rentobj, properties


# common functions
def get_combos_common():
    # This function returns values for comboboxes used by rents, queries and headrents
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenuredets = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]

    return advarrdets, freqdets, landlords, statusdets, tenuredets


def get_combos_rentonly():
    # This function returns the list values for various comboboxes used only by rents
    actypedets = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    mailtodets = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    salegradedets = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]

    return actypedets, deedcodes, mailtodets, salegradedets


def get_queryoptions_common():
    # return options for common multiple choice controls in home page and queries page
    advarrdets, freqdets, landlords, statusdets, tenuredets = get_combos_common()
    landlords.insert(0, "all landlords")
    statusdets.insert(0, "all statuses")
    tenuredets.insert(0, "all tenures")

    return landlords, statusdets, tenuredets

def get_queryoptions_advanced():
    # return options for advanced multiple choice controls in home page and queries page
    actypedets, deedcodes, mailtodets, salegradedets = get_combos_rentonly()
    salegradedets.insert(0, "all salegrades")
    actypedets.insert(0, "all actypes")
    floads = [value for (value,) in Jstore.query.with_entities(Jstore.name).all()]
    prdeliveries = [value for (value,) in Typeprdelivery.query.with_entities(Typeprdelivery.prdeliverydet).all()]
    options = ("Include", "Exclude", "Only")

    return actypedets, floads, options, prdeliveries, salegradedets


def get_idlist_recent(recent_field):
    id_list = [1, 51, 101, 151, 201, 251, 301, 351, 401, 451, 501]
    id_list = json.loads(getattr(current_user, recent_field)) if getattr(current_user, recent_field) else id_list

    return id_list


def pop_idlist_recent(recent_field, id):
    id_list = json.loads(getattr(current_user, recent_field))
    if id not in id_list:
        id_list.insert(0, id)
        if len(id_list) > 30:
            id_list.pop()
        setattr(current_user, recent_field, json.dumps(id_list))
        db.session.commit()


