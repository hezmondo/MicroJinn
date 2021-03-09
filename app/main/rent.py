import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from app.dao.charge import get_rent_charge_details
from app.main.common import inc_date_m
from app.main.functions import dateToStr, hashCode, money, moneyToStr, round_decimals_down


def get_rent_gale(next_rent_date, frequency, rentpa):
    if rentpa == 0 or frequency not in (2, 4):
        return money(rentpa)
    missing_pennies = (rentpa * 100) % frequency
    if missing_pennies == 0:
        return money(rentpa / frequency)
    rent_gale = money(round_decimals_down(rentpa / frequency))
    if (frequency == 2 and next_rent_date.month > 6) or (frequency == 4 and next_rent_date.month > 9):
        return rent_gale + (missing_pennies / 100)
    else:
        return money(rent_gale)


def get_rent_strings(rent, type='mail'):
    # this function creates strings needed for mail, pay requests and rent screen statements
    # first we test and manipulate certain items from rent
    paidtodate = rent.paidtodate if hasattr(rent, 'paidtodate') else datetime.date(1991, 1, 1)
    lastrentdate = rent.lastrentdate if hasattr(rent, 'lastrentdate') else datetime.date(1991, 1, 1)
    nextrentdate = inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, 1) if hasattr(rent,
                                'lastrentdate') else datetime.date(1991, 1, 1)
    nextrentdate_plus1 =  inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, 2) if hasattr(rent,
                                'lastrentdate') else datetime.date(1991, 1, 1)
    arrears = rent.arrears if rent.arrears else Decimal(0)
    arrears_start_date = dateToStr(paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(nextrentdate + relativedelta(days=-1)) \
        if rent.advarrdet == "in advance" else dateToStr(lastrentdate)
    arrearsenddate_plus1 = dateToStr(nextrentdate_plus1 + relativedelta(days=-1)) \
        if rent.advarrdet == "in advance" else dateToStr(nextrentdate)
    next_gale_start = dateToStr(nextrentdate) \
        if rent.advarrdet == "in advance" else dateToStr(lastrentdate + relativedelta(days=1))
    charges = get_rent_charge_details(rent.id) or Decimal(0)
    # TODO: charges_string needs cleaning adds ', ' onto final charge
    charges_string = "no charges"
    charges_list = []
    if charges and charges != 0:
        for charge in charges:
            charge_string = "{} {} added on {}".format(moneyToStr(charge.chargetotal, pound=True),
                                                       charge.chargedesc, dateToStr(charge.chargestartdate))
            charges_string += charge_string + ", "
            charges_list.append(charge_string)
    for_sale = rent.salegradedet if hasattr(rent, 'salegradedet') else "not for sale"
    rentpa = rent.rentpa if rent.rentpa else Decimal(1)
    rent_gale = get_rent_gale(nextrentdate, rent.freq_id, rentpa)
    rent_type = "rent charge" if rent.tenuredet == "rentcharge" else "ground rent"
    totcharges = rent.totcharges if rent.totcharges else Decimal(0)
    totdue = arrears + totcharges
    price = rent.price if rent.price else Decimal(0)
    if price != 0:
        days = (date.today() - paidtodate).days
        # days = Decimal(days)
        price_quote = price + totcharges + (days * rentpa / Decimal(365.25))
    else:
        price_quote = Decimal(99999)
    rent_strings_1 = {'#advarr#': rent.advarrdet if hasattr(rent, 'advarrdet') else "no advarrdet",
                      '#arrears#': moneyToStr(arrears, pound=True),
                      '#arrears_start_date#': arrears_start_date,
                      '#arrears_end_date#': arrears_end_date,
                      '#landlord_name#': rent.name if hasattr(rent, 'name') else "no landlord name",
                      '#lastrentdate#': dateToStr(rent.lastrentdate),
                      '#manageraddr#': rent.manageraddr if rent.manageraddr else "no manager address",
                      '#nextrentdate#': dateToStr(nextrentdate),
                      '#paidtodate#': dateToStr(paidtodate),
                      '#periodly#': rent.freqdet if rent.freqdet else "no periodly",
                      '#price_quote#': moneyToStr(price_quote, pound=True),
                      '#rentgale#': moneyToStr(rent_gale, pound=True),
                      '#rentpa#': moneyToStr(rent.rentpa, pound=True),
                      '#rent_type#': rent_type,
                      '#totcharges#': moneyToStr(totcharges, pound=True),
                      '#totdue#': moneyToStr(totdue, pound=True)
                      }
    rent_stat = get_rent_stat(rent, rent_strings_1)
    rent_owing = get_rent_owing(rent, rent_strings_1, nextrentdate)
    price_stat = "for sale at {}".format(moneyToStr(price_quote, pound=True)) \
        if for_sale == 'for sale' else "not for sale"
    rent_strings_2 = {'#acc_name#': rent.acc_name if hasattr(rent, 'acc_name') else "no acc_name",
                    '#acc_num#': rent.acc_num if hasattr(rent, 'acc_num') else "no acc_num",
                    '#arrearsenddate_plus1#': arrearsenddate_plus1,
                    '#bank_name#': rent.bank_name if hasattr(rent, 'bank_name') else "no bank_name",
                    '#charges_string#': charges_string,
                    '#hashcode#': hashCode(rent.rentcode) if hasattr(rent, 'rentcode') else "no hashcode",
                    '#manageraddr2#': rent.manageraddr2 if hasattr(rent, 'manageraddr2') else "no manageraddr2",
                    '#managername#': rent.managername if rent.managername else "no manager name",
                    '#next_gale_start#': next_gale_start,
                    '#nextrentdate_plus1#': dateToStr(nextrentdate_plus1),
                    '#pay_date#': dateToStr(date.today() + relativedelta(days=30)),
                    '#propaddr#': rent.propaddr if rent.propaddr else "no property address",
                    '#rentcode#': rent.rentcode if rent.rentcode else "no rentcode",
                    '#rent_stat#': rent_stat,
                    '#sort_code#': rent.sort_code if hasattr(rent, 'sort_code') else "no sort_code",
                    '#tenantname#': rent.tenantname if rent.tenantname else "no tenant name",
                    '#today#': dateToStr(date.today()),
                    }
    rent_strings_3 = {'#rent_owing#': rent_owing,
                    '#rent_stat#': rent_stat
                    }

    rent_strings_rent = {'charges_list': charges_list,
                         'price_stat': price_stat,
                         'rent_owing': rent_owing,
                         'rent_stat': rent_stat,
                         'nextrentdate': nextrentdate
                         }
    if type == 'rent':
        return rent_strings_rent
    elif type == 'payrequest':
        return {**rent_strings_1, **rent_strings_2}
    elif type == 'xray':
        rent_strings_xray = {'arrears': moneyToStr(arrears, pound=True),
                             'arrears_start_date': arrears_start_date,
                             'arrears_end_date': arrears_end_date,
                             'lastrentdate': dateToStr(rent.lastrentdate),
                             'nextrentdate': dateToStr(nextrentdate),
                             'paidtodate': dateToStr(paidtodate),
                             'price_quote': moneyToStr(price_quote, pound=True),
                             'rentgale': moneyToStr(rent_gale, pound=True),
                             'rent_owing': rent_owing,
                             'rentpa': moneyToStr(rent.rentpa, pound=True),
                             'rent_type': rent_type,
                             'totcharges': moneyToStr(totcharges, pound=True),
                             'totdue': moneyToStr(totdue, pound=True)
                             }
        return rent_strings_xray
    else:
        return {**rent_strings_1, **rent_strings_2, **rent_strings_3}


def get_rent_owing(rent, rent_strings, nextrentdate):
    if rent.statusdet not in ("grouped payment", "sold off", "terminated"):
        if rent.arrears == 0 and nextrentdate >= date.today():
            rent_owing = "There is no {0} owing to us on this property and {0} is paid up to {1}. \
                            Further {0} will be due and payable {2} {3} on {4} in the sum of {5}" \
                .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rent.arrears == 0 and nextrentdate < date.today():
            rent_owing = "{0} was last paid on this property up to {1}. Further {0} was due and \
                            payable {2} {3} on {4} in the sum of {5} but no rent demand has yet been issued." \
                .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rent.arrears > 0 and rent.lastrentdate > date.today():
            rent_owing = "A recent pay request has been issued for {} {} due {} {} on {}. \
            This amount is not payable until the date stated on the pay request." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#lastrentdate#"])
        else:
            rent_owing = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
             to {3}." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"])
        if rent.totcharges and rent.totcharges > 0:
            rent_owing = rent_owing.strip('.') + " plus other charges as set out below."
        # TODO reduced
    else:
        rent_owing = "no rent owing because the status for this rent is either grouped payment, managed, \
                        sold off or terminated"

    return rent_owing


def get_rent_stat(rent, rent_strings):
    if rent.statusdet in ("sold off", "terminated"):
        rent_stat = "This property has been sold off or terminated and was subject to a {} of {} " \
                    "per annum payable {} {}, last paid to {}." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"], rent_strings["#paidtodate#"])
    elif rent.statusdet in ("grouped payment", "managed"):
        rent_stat = "This property is subject to a {} of {} per annum payable {} {} but \
                        this rent is collected within a block rent or otherwise managed elsewhere." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"])
    else:
        rent_stat = "This property is subject to a {} of {} per annum payable {} {}." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"])

    return rent_stat
