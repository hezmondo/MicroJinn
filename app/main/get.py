from datetime import date
from flask import flash, redirect, url_for, request, session
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app.main.functions import commit_to_database
from app.models import Agent, Formletter, Headrent, Income, Incomealloc, Landlord, \
    Loan, Loan_statement, Manager, Money_category, Money_item, Rent, Rental, Rental_statement, \
    Typeadvarr, Money_account, Template, Typefreq, Typedoc, Typepayment, Typestatus, Typetenure, Emailaccount


# email accounts
def get_emailaccounts():
    emailaccs = Emailaccount.query.all()

    return emailaccs


def get_emailaccount(id):
    emailacc = Emailaccount.query.filter(Emailaccount.id == id).one_or_none()

    return emailacc


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
        formletters = Formletter.query.all()

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

def get_loans(action):
    if action == "Nick":
        loans = Loan.query.with_entities(Loan.id, Loan.code, Loan.interest_rate, Loan.end_date, Loan.lender, Loan.borrower,
                               Loan.notes, Loan.val_date, Loan.valuation, Loan.interestpa) \
            .filter(Loan.lender.ilike('%NJL%')).all()
        loansum = Loan.query.with_entities(func.sum(Loan.valuation).label('totval'),
                                           func.sum(Loan.interestpa).label('totint')) \
            .filter(Loan.lender.ilike('%NJL%')).first()
    else:
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


# common functions
def get_combos_common():
    # This function returns values for comboboxes used by rents, queries and headrents
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenuredets = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]

    return advarrdets, freqdets, landlords, statusdets, tenuredets
