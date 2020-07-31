import datetime
from app.main.common import readFromFile
from app.main.functions import dateToStr, hashCode, moneyToStr
from app.main.get import getmaildata, getrentobj_main
from app.main.functions import htmlSpecialMarkDown

def writeMail(rent_id, income_id, letter_id):
    # This function takes in rent details and outputs a mail item (letter/email)

    rentobj, properties, totcharges = getrentobj_main(rent_id)
    incomedata, allocdata, letterdata, addressdata = getmaildata(rent_id, income_id, letter_id)

    word_variables = {'#advarr#': rentobj.advarrdet if rentobj else "in elevence",
        '#arrears#': moneyToStr(rentobj.arrears if rentobj else 111.00, pound=True),
        '#hashcode#': hashCode(rentobj.rentcode) if rentobj else "some hashcode",
        '#landlordaddr#': addressdata.landlordaddr if addressdata else "some landlord address",
        '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/2011",
        '#lessor#': "rent charge owner" if rentobj.tenuredet == "rent charge" else "ground rent owner",
        '#manageraddr#': addressdata.manageraddr if addressdata else "some manager address",
        '#manageraddr2#': addressdata.manageraddr2 if addressdata else "some manager address2",
        '#nextrentdate#': dateToStr(rentobj.nextrentdate) if rentobj else "11/11/2011",
        '#paidtodate#': dateToStr(rentobj.paidtodate) if rentobj else "11/11/2011",
        '#payamount#': moneyToStr(incomedata.payamount if incomedata else 111.00, pound=True),
        '#paydate#': dateToStr(incomedata.paydate) if incomedata else "11/11/2011",
        '#payer#': incomedata.payer if incomedata else "some payer",
        '#paytypedet#': incomedata.paytypedet if incomedata else "somepaytype",
        '#periodly#': rentobj.freqdet if rentobj else "eleventhly",
        '#propaddr#': addressdata.propaddr if addressdata else "some property address",
        '#rentcode#': rentobj.rentcode if rentobj else "some rentcode",
        '#rentpa#': moneyToStr(rentobj.rentpa if rentobj else 11.00, pound=True),
        '#rent_type#': "rent charge" if rentobj.tenuredet == "rent charge" else "ground rent",
        '#Today#': dateToStr(datetime.date.today())
    }

    subject = letterdata.subject
    part1 = letterdata.part1 if letterdata.part1 else ""
    part2 = letterdata.part2 if letterdata.part2 else ""
    part3 = letterdata.part3 if letterdata.part3 else ""

    subject = doReplace(word_variables, subject)
    part1 = doReplace(word_variables, part1)
    part2 = doReplace(word_variables, part2)
    part3 = doReplace(word_variables, part3)

    mailaddr = addressdata.mailaddr
    mailaddr = mailaddr.split(", ")

    return subject, part1, part2, part3, rentobj, letterdata, addressdata, mailaddr


def doReplace(dict, clause):
    for key, value in dict.items():
        clause = clause.replace(key, value)

    return clause

     # word_variables = [
#         ('#BankName#', rent.landlord['BankName'] if rent else "Natwest RH"),
#         ('#BankSortCode#', rent.landlord['BankSortCode'] if rent else "00-00-00"),
#         ('#BankAccountNumber#', rent.landlord['BankAccountNumber'] if rent else "10101010"),
#         ('#BankAccountName#', rent.landlord['BankAccountName'] if rent else "R Hesmondhalgh & D Maloney"),
#         ('#ChargesStat#', rent.chargesStatement() if rent else ""),
#         ('#HashCode#', rent.hashCode() if rent else "Abracadabra"),
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
#         ('#RentCode#', rent.info['RentCode'] if rent else "DUMMY"),
#         ('#RentOwingPeriod#', "{} to {}".format(dateToStr(rent.arrearsStartDate()) if rent else "01/01/2012",
#                                                 dateToStr(rent.arrearsEndDate()) if rent else "31/12/2012")),
#         ('#RentOwingPeriodStart#', dateToStr(rent.arrearsStartDate()) if rent else "01/01/2012"),
#         ('#RentOwingPeriodEnd#', dateToStr(rent.arrearsEndDate()) if rent else "01/01/2014"),
#         ('#PayRequestRentPeriod#', "{} to {}".format(dateToStr(tot_rent_start_date) if rent else "01/01/2012",
#                                                      dateToStr(period_end_date) if rent else "01/06/2013")),
#         ('#Source#', rent.info['Source'] if rent else "Source"),
#         ('#TenantName#', rent.info['TenantName'] if rent else "Joe Smith"),
#         ('#TenureType#', rent.tenure() if rent else "leasehold"),
#         ('#Today#', dateToStr(today) if rent else dateToStr(today)),
#         ('#TotCharges#', moneyToStr(rent.info['ChargesBalance'] if rent else 999.99, pound=True)),
#         ('#TotalDue#', moneyToStr(tot if rent else 80.00, pound=True)),
#     ]
#
#     # Currently handling receipt statement differently because I didn't want to pass word variables a DbHandler,
#     # but this might be changed, especially when considering letters without a rent
#
#     return {x: y for x, y in word_variables}
