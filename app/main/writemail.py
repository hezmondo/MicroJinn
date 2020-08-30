import datetime
from flask import request
from decimal import Decimal
from app.main.common import readFromFile
from app.main.functions import dateToStr, hashCode, moneyToStr, money
from app.main.get import get_doc, get_leasedata, getmaildata, getrentobj_main
from app.main.functions import htmlSpecialMarkDown

def writeMail(rent_id, income_id, doc_id, type):
    # Get rent/prop/income details and output mail (letter/payrequest/account/email/invoice/rem adv)
    rentobj, properties = getrentobj_main(rent_id)
    incomedata, allocdata, bankdata, addressdata = getmaildata(rent_id, income_id)
    doc = get_doc(doc_id)
    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    totdue = arrears + totcharges

    word_variables = {'#advarr#': rentobj.advarrdet if rentobj else "in elevence",
        '#accname#': bankdata.accname if bankdata else "some accname",
        '#accnum#': bankdata.accnum if bankdata else "some accnumber",
        '#sortcode#': bankdata.sortcode if bankdata else "some sortcode",
        '#bankname#': bankdata.bankname if bankdata else "some bankname",
        '#arrears#': moneyToStr(arrears, pound=True),
        '#hashcode#': hashCode(rentobj.rentcode) if rentobj else "some hashcode",
        '#landlordaddr#': addressdata.landlordaddr if addressdata else "some landlord address",
        '#landlordname#': rentobj.landlordname if rentobj else "some landlord name",
        '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/2011",
        '#lessor#': "rent charge owner" if rentobj.tenuredet == "rent charge" else "ground rent owner",
        '#managername#': rentobj.managername if rentobj else "some manager name",
        '#manageraddr#': addressdata.manageraddr if addressdata else "some manager address",
        '#manageraddr2#': addressdata.manageraddr2 if addressdata else "some manager address2",
        '#nextrentdate#': dateToStr(rentobj.nextrentdate) if rentobj else "11/11/2011",
        '#paidtodate#': dateToStr(rentobj.paidtodate) if rentobj else "11/11/2011",
        '#payamount#': moneyToStr(incomedata.payamount, pound=True),
        '#paydate#': dateToStr(incomedata.paydate) if incomedata else "11/11/2011",
        '#payer#': incomedata.payer if incomedata else "some payer",
        '#paytypedet#': incomedata.paytypedet if incomedata else "somepaytype",
        '#periodly#': rentobj.freqdet if rentobj else "eleventhly",
        '#propaddr#': rentobj.propaddr if rentobj else "some property address",
        '#rentcode#': rentobj.rentcode if rentobj else "some rentcode",
        '#rentpa#': moneyToStr(rentobj.rentpa if rentobj else 1111.00, pound=True),
        '#rent_type#': "rent charge" if rentobj.tenuredet == "rent charge" else "ground rent",
        '#tenantname#': rentobj.tenantname if rentobj else "some tenant name",
        '#totcharges#': moneyToStr(totcharges, pound=True),
        '#totdue#': moneyToStr(totdue if totdue else 1111.00, pound=True),
        '#today#': dateToStr(datetime.date.today())
    }
    if type == "lease":
        fh_rate = request.form['fh_rate']
        gr_rate = request.form['gr_rate']
        new_gr_a = request.form['new_gr_a']
        new_gr_b = request.form['new_gr_b']
        yp_low = request.form['yp_low']
        yp_high = request.form['yp_high']

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

    subject = doc.subject
    part1 = doc.part1 if doc.part1 else ""
    part2 = doc.part2 if doc.part2 else ""
    part3 = doc.part3 if doc.part3 else ""

    subject = doReplace(word_variables, subject)
    part1 = doReplace(word_variables, part1)
    part2 = doReplace(word_variables, part2)
    part3 = doReplace(word_variables, part3)

    return subject, part1, part2, part3, rentobj, doc, addressdata, leasedata


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
