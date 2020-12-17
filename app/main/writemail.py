import datetime
from flask import request
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from app.main.common import readFromFile
from app.main.functions import dateToStr, hashCode, moneyToStr, money
from app.main.rent_obj import get_leasedata, getrentobj_main
from app.main.other import get_formletter, get_formpayrequest, getmaildata
from app.main.payrequests import PayRequestTable, build_pr_table, get_payrequest_table_charges, \
    get_rent_statement, get_arrears_statement, check_or_add_recovery_charge
# from app.models import Pr_arrears_matrix
from app.main.functions import htmlSpecialMarkDown


def writeMail(rent_id, income_id, formletter_id, action):
    # Get rent/prop/income details and output mail (letter/payrequest/account/email/invoice/rem adv)
    rentobj, properties = getrentobj_main(rent_id)
    incomedata, allocdata, bankdata, addressdata = getmaildata(rent_id, income_id)

    formletter = get_formletter(formletter_id)

    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(rentobj.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rentobj.nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(rentobj.lastrentdate)
    # TODO: Check if rentobj.tenuredet == "Rentcharge" below
    rent_type = "rent charge" if rentobj.tenuredet == "rent charge" else "ground rent"
    totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    totdue = arrears + totcharges

    word_variables = {'#advarr#': rentobj.advarrdet if rentobj else "no advarr",
        '#accname#': bankdata.accname if bankdata else "no accname",
        '#accnum#': bankdata.accnum if bankdata else "no accnumber",
        '#sortcode#': bankdata.sortcode if bankdata else "no sortcode",
        '#bankname#': bankdata.bankname if bankdata else "no bankname",
        '#arrears#': moneyToStr(arrears, pound=True),
        '#hashcode#': hashCode(rentobj.rentcode) if rentobj else "no hashcode",
        '#landlordaddr#': addressdata.landlordaddr if addressdata else "no landlord address",
        '#landlordname#': rentobj.landlordname if rentobj else "no landlord name",
        '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/1111",
        '#lessor#': "rent charge owner" if rentobj.tenuredet == "rent charge" else "ground rent owner",
        '#managername#': rentobj.managername if rentobj else "no manager name",
        '#manageraddr#': addressdata.manageraddr if addressdata else "no manager address",
        '#manageraddr2#': addressdata.manageraddr2 if addressdata else "no manager address2",
        '#nextrentdate#': dateToStr(rentobj.nextrentdate) if rentobj else "no nextrentdate",
        '#paidtodate#': dateToStr(rentobj.paidtodate) if rentobj else "no paidtodate",
        '#payamount#': moneyToStr(incomedata.payamount, pound=True) if incomedata else "no payment",
        '#paydate#': dateToStr(incomedata.paydate) if incomedata else "no paydate",
        '#payer#': incomedata.payer if incomedata else "no payer",
        '#paytypedet#': incomedata.paytypedet if incomedata else "no paytype",
        '#periodly#': rentobj.freqdet if rentobj else "no periodly",
        '#propaddr#': rentobj.propaddr if rentobj else "no property address",
        '#rentcode#': rentobj.rentcode if rentobj else "no rentcode",
        '#arrears_start_date#': arrears_start_date,
        '#arrears_end_date#': arrears_end_date,
        '#rentpa#': moneyToStr(rentobj.rentpa, pound=True) if rentobj else "no rent",
        '#rent_type#': rent_type,
        '#tenantname#': rentobj.tenantname if rentobj else "no tenant name",
        '#totcharges#': moneyToStr(totcharges, pound=True),
        '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due",
        '#today#': dateToStr(datetime.date.today())
    }
    if action == "lease":
        fh_rate = request.form.get('fh_rate')
        gr_rate = request.form.get('gr_rate')
        new_gr_a = request.form.get('new_gr_a')
        new_gr_b = request.form.get('new_gr_b')
        yp_low = request.form.get('yp_low')
        yp_high = request.form.get('yp_high')

        leasedata = get_leasedata(rent_id, fh_rate, gr_rate, new_gr_a, new_gr_b, yp_low, yp_high)
        impval = leasedata["impvalk"] * 1000
        unimpval = leasedata["impvalk"] * leasedata["realty"] * 10
        lease_variables = {'#unexpired#': str(leasedata["unexpired"]) if leasedata else "11.11",
                '#rent_code#': leasedata["rent_code"] if leasedata else "some rentcode",
                '#relativity#': str(leasedata["realty"]) if leasedata else "some rentcode",
                '#totval#': str(leasedata["totval"]) if leasedata else "some rentcode",
                '#unimpvalue#': moneyToStr(unimpval if leasedata else 555.55, pound=True),
                '#impvalue#': moneyToStr(impval if leasedata else 555.55, pound=True),
                '#leq99a#': moneyToStr(leasedata["leq99a"] if leasedata else 55555.55, pound=True),
                '#grnewa#': moneyToStr(leasedata["grnew1"] if leasedata else 555.55, pound=True),
                '#grnewb#': moneyToStr(leasedata["grnew2"] if leasedata else 555.55, pound=True),
                '#leq125a#': moneyToStr(leasedata["leq125a"] if leasedata else 55555.55, pound=True),
                '#leq175a#': moneyToStr(leasedata["leq175a"] if leasedata else 55555.55, pound=True),
                '#leq175f#': moneyToStr(leasedata["leq175f"] if leasedata else 55555.55, pound=True),
                '#leq175p#': moneyToStr(leasedata["leq175p"] if leasedata else 55555.55, pound=True),
                           }
        word_variables.update(lease_variables)
    else:
        leasedata = None

    subject = formletter.subject
    block = formletter.block if formletter.block else ""
    doctype = formletter.desc
    dcode = formletter.code

    subject = doReplace(word_variables, subject)
    block = doReplace(word_variables, block)

    return addressdata, block, leasedata, rentobj, subject, doctype, dcode


# TODO: refactor - some duplication of writeMail (above)
def write_payrequest(rent_id, formpayrequest_id):
    rentobj, properties = getrentobj_main(rent_id)

    check_or_add_recovery_charge(rentobj)

    # TODO: Can we avoid passing 0 to getmaildata
    incomedata, allocdata, bankdata, addressdata = getmaildata(rent_id, 0)

    form_payrequest = get_formpayrequest(formpayrequest_id)

    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(rentobj.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rentobj.nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(rentobj.lastrentdate)
    rent_type = "rent charge" if rentobj.tenuredet == "Rentcharge" else "ground rent"
    #  totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    rent_gale = (rentobj.rentpa / rentobj.freq_id) if rentobj.rentpa != 0 else 0

    list_table_amounts = {}
    if rent_gale:
        rent_statement = get_rent_statement(rentobj, rent_type)
        list_table_amounts.update({rent_statement: rent_gale})
    if arrears:
        arrears_statement = get_arrears_statement(rent_type, arrears_start_date, arrears_end_date)
        list_table_amounts.update({arrears_statement: arrears})
    # TODO: Charges can be calculated in rentobj/payrequests.py rather than separately using a function here
    charges, totcharges = get_payrequest_table_charges(rent_id)

    if totcharges:
        list_table_amounts.update(charges)

    totdue = rent_gale + arrears + totcharges
    list_table_amounts.update({'The total amount payable is:': totdue})

    word_variables = {'#advarr#': rentobj.advarrdet if rentobj else "no advarr",
                      '#accname#': bankdata.accname if bankdata else "no accname",
                      '#accnum#': bankdata.accnum if bankdata else "no accnumber",
                      '#sortcode#': bankdata.sortcode if bankdata else "no sortcode",
                      '#bankname#': bankdata.bankname if bankdata else "no bankname",
                      '#arrears#': moneyToStr(arrears, pound=True),
                      '#hashcode#': hashCode(rentobj.rentcode) if rentobj else "no hashcode",
                      '#landlordaddr#': addressdata.landlordaddr if addressdata else "no landlord address",
                      '#landlordname#': rentobj.landlordname if rentobj else "no landlord name",
                      '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/1111",
                      '#lessor#': "rent charge owner" if rentobj.tenuredet == "rent charge" else "ground rent owner",
                      '#managername#': rentobj.managername if rentobj else "no manager name",
                      '#manageraddr#': addressdata.manageraddr if addressdata else "no manager address",
                      '#manageraddr2#': addressdata.manageraddr2 if addressdata else "no manager address2",
                      '#nextrentdate#': dateToStr(rentobj.nextrentdate) if rentobj else "no nextrentdate",
                      '#paidtodate#': dateToStr(rentobj.paidtodate) if rentobj else "no paidtodate",
                      '#payamount#': moneyToStr(incomedata.payamount, pound=True) if incomedata else "no payment",
                      '#paydate#': dateToStr(incomedata.paydate) if incomedata else "no paydate",
                      '#payer#': incomedata.payer if incomedata else "no payer",
                      '#paytypedet#': incomedata.paytypedet if incomedata else "no paytype",
                      '#periodly#': rentobj.freqdet if rentobj else "no periodly",
                      '#propaddr#': rentobj.propaddr if rentobj else "no property address",
                      '#rentcode#': rentobj.rentcode if rentobj else "no rentcode",
                       '#arrears_start_date#': arrears_start_date,
                       '#arrears_end_date#': arrears_end_date,
                      '#rentpa#': moneyToStr(rentobj.rentpa, pound=True) if rentobj else "no rent",
                       # '#rent_type#': rent_type,
                      '#tenantname#': rentobj.tenantname if rentobj else "no tenant name",
                       # '#totcharges#': moneyToStr(totcharges, pound=True),
                      '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due",

                      '#today#': dateToStr(datetime.date.today())
                      }

    subject = "{} account for property: #propaddr#".format(rent_type.capitalize())
    subject = doReplace(word_variables, subject)
    block = form_payrequest.block if form_payrequest.block else ""
    block = doReplace(word_variables, block)

    items = build_pr_table(list_table_amounts)
    table = PayRequestTable(items)

    return addressdata, block, rentobj, subject, table, totdue


def doReplace(dict, clause):
    for key, value in dict.items():
        clause = clause.replace(key, value)

    return clause

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
