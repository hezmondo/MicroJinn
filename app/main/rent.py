import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from app.dao.charge import get_rent_charge_details
from app.dao.functions import dateToStr, hashCode, moneyToStr


def get_rent_strings(rentobj, type='mail'):
    # this function creates strings needed for mail, pay requests and rent screen statements
    # first we test and manipulate certain items from rentobj
    paidtodate = rentobj.paidtodate if hasattr(rentobj, 'paidtodate') else  datetime.date(1991, 1, 1)
    lastrentdate = rentobj.lastrentdate if hasattr(rentobj, 'lastrentdate') else datetime.date(1991, 1, 1)
    nextrentdate = rentobj.nextrentdate if hasattr(rentobj, 'lastrentdate') else datetime.date(1991, 1, 1)
    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(lastrentdate)
    charges = get_rent_charge_details(rentobj.id) or Decimal(0)
    charges_list = "no charges"
    if charges and charges != 0:
        # charges_list = ""
        # for charge in charges:
        #     charges_list += "{} {} added on {}, ".format(moneyToStr(charge.chargetotal, pound=True),
        #                                                charge.chargedesc, dateToStr(charge.chargestartdate))
        # charges_list = [x.strip() for x in charges_list.split(', ')]
        charges_list = []
        for charge in charges:
            charges_list.append("{} {} added on {}".format(moneyToStr(charge.chargetotal, pound=True),
                                                       charge.chargedesc, dateToStr(charge.chargestartdate)))
    for_sale = rentobj.salegradedet if hasattr(rentobj, 'salegradedet') else "not for sale"
    rentpa = rentobj.rentpa if rentobj.rentpa else Decimal(1)
    frequency = rentobj.freq_id if rentobj.freq_id else 1
    rent_gale = (rentpa / frequency)
    rent_type = "rent charge" if rentobj.tenuredet == "rentcharge" else "ground rent"
    totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    totdue = arrears + totcharges
    price = rentobj.price if rentobj.price else Decimal(0)
    if price != 0:
        days = (date.today() - paidtodate).days
        # days = Decimal(days)
        price_quote = price + totcharges + (days*rentpa / Decimal(365.25))
    else:
        price_quote = Decimal(99999)
    rent_strings_1 = {'#advarr#': rentobj.advarrdet if hasattr(rentobj, 'advarrdet') else "no advarrdet",
                    '#arrears#': moneyToStr(arrears, pound=True),
                    '#arrears_start_date#': arrears_start_date,
                    '#arrears_end_date#': arrears_end_date,
                    '#landlord_name#': rentobj.name if hasattr(rentobj, 'name') else "no landlord name",
                    '#manageraddr#': rentobj.manageraddr if rentobj.manageraddr else "no manager address",
                    '#nextrentdate#': dateToStr(rentobj.nextrentdate),
                    '#paidtodate#': dateToStr(paidtodate),
                    '#periodly#': rentobj.freqdet if rentobj.freqdet else "no periodly",
                    '#price_quote#': moneyToStr(price_quote, pound=True),
                    '#rentgale#': moneyToStr(rent_gale, pound=True),
                    '#rentpa#': moneyToStr(rentobj.rentpa, pound=True),
                    '#rent_type#': rent_type,
                    '#totcharges#': moneyToStr(totcharges, pound=True),
                    '#totdue#': moneyToStr(totdue, pound=True)
                    }
    rent_stat = get_rent_stat(rentobj, rent_strings_1)
    rent_owing = get_rent_owing(rentobj, rent_strings_1)
    price_stat = "for sale at {}".format(moneyToStr(price_quote, pound=True)) \
                        if for_sale == 'for sale' else "not for sale"
    rent_strings_2 = {'#acc_name#': rentobj.acc_name if hasattr(rentobj, 'acc_name') else "no acc_name",
                    '#acc_num#': rentobj.acc_num if hasattr(rentobj, 'acc_num') else "no acc_num",
                    '#bank_name#': rentobj.bank_name if hasattr(rentobj, 'bank_name') else "no bank_name",
                    '#charges_list#': charges_list,
                    '#hashcode#': hashCode(rentobj.rentcode) if hasattr(rentobj, 'rentcode') else "no hashcode",
                    '#lastrentdate#': dateToStr(rentobj.lastrentdate),
                    '#manageraddr2#': rentobj.manageraddr2 if hasattr(rentobj, 'manageraddr2') else "no manageraddr2",
                    '#managername#': rentobj.managername if rentobj.managername else "no manager name",
                    '#propaddr#': rentobj.propaddr if rentobj.propaddr else "no property address",
                    '#rentcode#': rentobj.rentcode if rentobj.rentcode else "no rentcode",
                    '#rent_stat#': rent_stat,
                    '#sort_code#': rentobj.sort_code if hasattr(rentobj, 'sort_code') else "no sort_code",
                    '#tenantname#': rentobj.tenantname if rentobj.tenantname else "no tenant name",
                    '#today#': dateToStr(date.today()),
                    }
    rent_strings_3 = {'#charges_list#': charges_list,
                    '#rent_owing#': rent_owing,
                    '#rent_stat#': rent_stat
                    }

    rent_strings_rent = {'charges_list': charges_list,
                           'price_stat': price_stat,
                           'rent_owing': rent_owing,
                           'rent_stat': rent_stat
                           }
    if type == 'rent':
        return rent_strings_rent
    elif type == 'payrequest':
        return {**rent_strings_1, **rent_strings_2}
    else:
        return {**rent_strings_1, **rent_strings_2, **rent_strings_3}


def get_rent_owing(rentobj, rent_strings):
    if rentobj.statusdet not in ("grouped payment", "sold off", "terminated"):
        if rentobj.arrears == 0 and rentobj.nextrentdate >= date.today():
            rent_owing = "There is no {0} owing to us on this property and {0} is paid up to {1}. \
                            Further {0} will be due and payable {2} {3} on {4} in the sum of {5}"\
                    .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                            rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears == 0 and rentobj.nextrentdate < date.today():
            rent_owing = "{0} was last paid on this property up to {1}. Further {0} was due and \
                            payable {2} {3} on {4} in the sum of {5} but no rent demand has yet been issued." \
                .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                            rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears > 0 and rentobj.lastrentdate > date.today():
            rent_owing = "A recent pay request has been issued for {} {} due {} {} on {}. \
            This amount is not payable until the date stated on the pay request."\
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#periodly#"],
                            rent_strings["#advarr#"], rent_strings["#nextrentdate#"])
        else:
            rent_owing = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
             to {3}." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"])
        if rentobj.totcharges and rentobj.totcharges > 0:
            rent_owing = rent_owing.strip('.') + " plus other charges as set out below."
        # TODO reduced
    else:
        rent_owing = "no rent owing because the status for this rent is either grouped payment, managed, \
                        sold off or terminated"

    return rent_owing


def get_rent_stat(rentobj, rent_strings):
    if rentobj.statusdet in ("sold off", "terminated"):
        rent_stat = "This property has been sold off or terminated and was subject to a {} of {} " \
                     "per annum payable {} {}, last paid to {}."\
                .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#paidtodate#"])
    elif rentobj.statusdet in ("grouped payment", "managed"):
        rent_stat = "This property is subject to a {} of {} per annum payable {} {} but \
                        this rent is collected within a block rent or otherwise managed elsewhere." \
                .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"])
    else:
        rent_stat = "This property is subject to a {} of {} per annum payable {} {}." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"])

    return rent_stat


