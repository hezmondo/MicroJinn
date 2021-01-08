import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from sqlalchemy import desc, func
from app.models import Charge, Chargetype, Income, Incomealloc, Landlord, Manager, Money_account, Rent, Typepayment
from app.main.functions import dateToStr, hashCode, moneyToStr, money
from app.main.lease import get_lease_variables
from app.main.rentobject import get_rentobject
from app.main.form_letter import get_formletter, get_formpayrequest
from app.main.payrequest import get_payrequest_table_charges, \
    get_rent_statement, get_arrears_statement, check_or_add_recovery_charge


# mail
def getmaildata(rent_id, income_id=0):
    if income_id == 0:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                                                                                    Income.date.label("paydate"),
                                                                                    Income.amount.label("payamount"),
                                                                                    Typepayment.paytypedet) \
            .filter(Incomealloc.rent_id == rent_id).order_by(desc(Income.date)).limit(1).one_or_none()
        # income_id = incomedata.id
    else:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                                                                                    Income.date.label("paydate"),
                                                                                    Income.amount.label("payamount"),
                                                                                    Typepayment.paytypedet) \
            .filter(Income.id == income_id).first()
    # allocdata = Incomealloc.join(Chargetype).with_entities(Incomealloc.id, Incomealloc.income_id,
    #                     Incomealloc.rentcode, Incomealloc.amount.label("alloctot"),
    #                     Chargetype.chargedesc).filter(Incomealloc.income_id == income_id).all()
    allocdata = None
    bankdata = Money_account.query.join(Landlord).join(Rent).with_entities(Money_account.accname, Money_account.accnum,
                                                                           Money_account.sortcode,
                                                                           Money_account.bankname).filter(
        Rent.id == rent_id) \
        .one_or_none()
    addressdata = Landlord.query.join(Rent).join(Manager).with_entities(
        Landlord.landlordaddr, Manager.manageraddr, Manager.manageraddr2,
    ).filter(Rent.id == rent_id).one_or_none()

    return incomedata, allocdata, bankdata, addressdata


def writeMail(rent_id, income_id, formletter_id, action):
    addressdata, rentobject, word_variables = get_word_variables(rent_id, income_id)
    formletter = get_formletter(formletter_id)

    if action == "lease":
        leasedata, lease_variables = get_lease_variables(rent_id)
        word_variables.update(lease_variables)
    else:
        leasedata = None

    subject = formletter.subject
    block = formletter.block if formletter.block else ""
    doctype = formletter.desc
    dcode = formletter.code

    subject = doReplace(word_variables, subject)
    block = doReplace(word_variables, block)

    return addressdata, block, leasedata, rentobject, subject, doctype, dcode


# TODO: We may need a get_pr_variables function later
def write_payrequest(rent_id, formpayrequest_id):
    addressdata, rentobject, word_variables = get_word_variables(rent_id)

    check_or_add_recovery_charge(rentobject)

    rent_gale = (rentobject.rentpa / rentobject.freq_id) if rentobject.rentpa != 0 else 0
    arrears = rentobject.arrears
    arrears_start_date = word_variables.get('#arrears_start_date#')
    arrears_end_date = word_variables.get('#arrears_end_date#')
    rent_type = word_variables.get('#rent_type#')

    table_rows = {}
    if rent_gale:
        rent_statement = get_rent_statement(rentobject, rent_type)
        table_rows.update({rent_statement: moneyToStr(rent_gale, pound=True)})
    if arrears:
        arrears_statement = get_arrears_statement(rent_type, arrears_start_date, arrears_end_date)
        table_rows.update({arrears_statement: moneyToStr(arrears, pound=True)})
    # TODO: Charges can be calculated in rentobject/payrequest.py rather than separately using a function here
    charges, totcharges = get_payrequest_table_charges(rent_id)
    if totcharges:
        table_rows.update(charges)
    totdue = rent_gale + arrears + totcharges
    totdue_string = moneyToStr(totdue, pound=True) if totdue else "no total due"

    subject = "{} account for property: #propaddr#".format(rent_type.capitalize())
    subject = doReplace(word_variables, subject)

    form_payrequest = get_formpayrequest(formpayrequest_id)
    block = form_payrequest.block if form_payrequest.block else ""
    block = doReplace(word_variables, block)

    return addressdata, block, rentobject, subject, table_rows, totdue, totdue_string


def doReplace(dict, clause):
    for key, value in dict.items():
        clause = clause.replace(key, value)

    return clause


def get_word_variables(rent_id, income_id=0):
    rentobject, properties = get_rentobject(rent_id)
    incomedata, allocdata, bankdata, addressdata = getmaildata(rent_id, income_id)

    arrears = rentobject.arrears if rentobject.arrears else Decimal(0)
    arrears_start_date = dateToStr(rentobject.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rentobject.nextrentdate + relativedelta(days=-1)) \
        if rentobject.advarrdet == "in advance" else dateToStr(rentobject.lastrentdate)
    # TODO: Check if rentobject.tenuredet == "Rentcharge" below
    rent_type = "rent charge" if rentobject.tenuredet == "rent charge" else "ground rent"
    totcharges = rentobject.totcharges if rentobject.totcharges else Decimal(0)
    totdue = arrears + totcharges

    word_variables = {'#advarr#': rentobject.advarrdet if rentobject else "no advarr",
                      '#accname#': bankdata.accname if bankdata else "no accname",
                      '#accnum#': bankdata.accnum if bankdata else "no accnumber",
                      '#sortcode#': bankdata.sortcode if bankdata else "no sortcode",
                      '#bankname#': bankdata.bankname if bankdata else "no bankname",
                      '#arrears#': moneyToStr(arrears, pound=True),
                      '#hashcode#': hashCode(rentobject.rentcode) if rentobject else "no hashcode",
                      '#landlordaddr#': addressdata.landlordaddr if addressdata else "no landlord address",
                      '#landlordname#': rentobject.landlordname if rentobject else "no landlord name",
                      '#lastrentdate#': dateToStr(rentobject.lastrentdate) if rentobject else "11/11/1111",
                      '#lessor#': "rent charge owner" if rentobject.tenuredet == "rent charge" else "ground rent owner",
                      '#managername#': rentobject.managername if rentobject else "no manager name",
                      '#manageraddr#': addressdata.manageraddr if addressdata else "no manager address",
                      '#manageraddr2#': addressdata.manageraddr2 if addressdata else "no manager address2",
                      '#nextrentdate#': dateToStr(rentobject.nextrentdate) if rentobject else "no nextrentdate",
                      '#paidtodate#': dateToStr(rentobject.paidtodate) if rentobject else "no paidtodate",
                      '#payamount#': moneyToStr(incomedata.payamount, pound=True) if incomedata else "no payment",
                      '#paydate#': dateToStr(incomedata.paydate) if incomedata else "no paydate",
                      '#payer#': incomedata.payer if incomedata else "no payer",
                      '#paytypedet#': incomedata.paytypedet if incomedata else "no paytype",
                      '#periodly#': rentobject.freqdet if rentobject else "no periodly",
                      '#propaddr#': rentobject.propaddr if rentobject else "no property address",
                      '#rentcode#': rentobject.rentcode if rentobject else "no rentcode",
                      '#arrears_start_date#': arrears_start_date,
                      '#arrears_end_date#': arrears_end_date,
                      '#rentpa#': moneyToStr(rentobject.rentpa, pound=True) if rentobject else "no rent",
                      '#rent_type#': rent_type,
                      '#tenantname#': rentobject.tenantname if rentobject else "no tenant name",
                      '#totcharges#': moneyToStr(totcharges, pound=True),
                      '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due",
                      '#today#': dateToStr(datetime.date.today())
                      }

    return addressdata, rentobject, word_variables


     # word_variables = [
#         ('#ChargesStat#', rent.chargesStatement() if rent else ""),
#         ('#NFee#', moneyToStr(rent.info['NFeeTotal'] if rent else 15.00, pound=True)),
#         ('#NextRentStat#', rent.nextRentStatement() if rent else ""),
#         ('#OwingStat#', rent.newOwingStatement() if rent else ""),
#         ('#Period#', rent.wordPeriodShort() if rent else "half-year or quarter-year e.g.\n'due #Period#ly' = 'due half-yearly'\n'one #Period#'s rent' = 'one half-year's rent'"),
#         ('#PeriodRent#', moneyToStr(period_rent if rent else 12.50, pound=True)),
#         ('#PeriodRentDouble#', moneyToStr(2 * period_rent if rent else 12.50, pound=True)),
#         # ('#PriceBase#', moneyToStr(rent.info['PriceBase'] if rent else 999999.99, pound=True)),
#         ('#Price#', moneyToStr(rent.priceFull() if rent else 999999.99, pound=True)),
#         ('#PricePM#', moneyToStr(rent.pricePM() if rent else 999999.99, pound=True)),
#         ('#ReceiptStat#', "PLACEHOLDER" if rent else "charge details on separate lines"),
#         # THis statement can only be generated
#         # with a specific receipt ID passed, therefore is found at 'run-time' rather than always being accessible
#         ('#RedRent#', rent.reducedRent(False) if rent else 'numerical reduced rent'),
#         ('#RedRentStat#', rent.redRenStatement() if rent else "one sentence statement describing reduced rent"),
#         ('#RentOwingPeriod#', "{} to {}".format(dateToStr(rent.arrearsStartDate()) if rent else "01/01/2012",
#                                                 dateToStr(rent.arrearsEndDate()) if rent else "31/12/2012")),
#         ('#RentOwingPeriodStart#', dateToStr(rent.arrearsStartDate()) if rent else "01/01/2012"),
#         ('#RentOwingPeriodEnd#', dateToStr(rent.arrearsEndDate()) if rent else "01/01/2014"),
#         ('#PayRequestRentPeriod#', "{} to {}".format(dateToStr(tot_rent_start_date) if rent else "01/01/2012",
#                                                      dateToStr(period_end_date) if rent else "01/06/2013")),
#         ('#Source#', rent.info['Source'] if rent else "Source"),
#     ]
#
#     # Currently handling receipt statement differently because I didn't want to pass word variables a DbHandler,
#     # but this might be changed, especially when considering letters without a rent
#
#     return {x: y for x, y in word_variables}
