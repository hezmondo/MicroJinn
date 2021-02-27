import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from app.dao.charge import get_rent_charge_details
from app.dao.functions import dateToStr, hashCode, moneyToStr


def get_rent_strings(rentobj, type='mail'):
    paidtodate = rentobj.paidtodate if hasattr(rentobj, 'paidtodate') else  datetime.datetime(1991, 1, 1)
    lastrentdate = rentobj.lastrentdate if hasattr(rentobj, 'lastrentdate') else datetime.datetime(1991, 1, 1)
    nextrentdate = rentobj.nextrentdate if hasattr(rentobj, 'lastrentdate') else datetime.datetime(1991, 1, 1)
    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(lastrentdate)
    charges = get_rent_charge_details(rentobj.id) or Decimal(0)
    charges_list = ""
    for charge in charges:
        charges_list += "{} {} added on {}, ".format(moneyToStr(charge.chargetotal, pound=True),
                                                   charge.chargedesc, dateToStr(charge.chargestartdate))
    charges_list = [x.strip() for x in charges_list.split(', ')]
    rentpa = rentobj.rentpa if rentobj.rentpa else Decimal(1)
    frequency = rentobj.freq_id if rentobj.freq_id else 1
    rent_gale = (rentpa / frequency)
    rent_type = "rent charge" if rentobj.tenuredet == "rentcharge" else "ground rent"
    totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    totdue = arrears + totcharges
    rent_strings_1 = {'#advarr#': rentobj.advarrdet if hasattr(rentobj, 'advarrdet') else "no advarrdet",
                    '#arrears#': moneyToStr(arrears, pound=True),
                    '#arrears_start_date#': arrears_start_date,
                    '#arrears_end_date#': arrears_end_date,
                    '#landlord_name#': rentobj.name if hasattr(rentobj, 'name') else "no landlord name",
                    '#manageraddr#': rentobj.manageraddr if rentobj.manageraddr else "no manager address",
                    '#nextrentdate#': dateToStr(rentobj.nextrentdate),
                    '#paidtodate#': dateToStr(paidtodate),
                    '#periodly#': rentobj.freqdet if rentobj.freqdet else "no periodly",
                    '#rentgale#': moneyToStr(rent_gale, pound=True),
                    '#rentpa#': moneyToStr(rentobj.rentpa, pound=True),
                    '#rent_type#': rent_type,
                    '#totcharges#': moneyToStr(totcharges, pound=True),
                    '#totdue#': moneyToStr(totdue, pound=True)
                    }
    rent_stat = get_rent_stat(rentobj, rent_strings_1)
    owing_stat = get_owing_stat(rentobj, rent_strings_1)
    rent_strings_2 = {'#acc_name#': rentobj.acc_name if hasattr(rentobj, 'acc_name') else "no acc_name",
                    '#acc_num#': rentobj.acc_num if hasattr(rentobj, 'acc_num') else "no acc_num",
                    '#bank_name#': rentobj.bank_name if hasattr(rentobj, 'bank_name') else "no bank_name",
                    '#charges_list#': charges_list,
                    '#hashcode#': hashCode(rentobj.rentcode) if hasattr(rentobj, 'rentcode') else "no hashcode",
                    '#lastrentdate#': dateToStr(rentobj.lastrentdate),
                    '#manageraddr2#': rentobj.manageraddr2 if hasattr(rentobj, 'manageraddr2') else "no manageraddr2",
                    '#managername#': rentobj.managername if rentobj.managername else "no manager name",
                    '#owing_stat#': owing_stat,
                    '#propaddr#': rentobj.propaddr if rentobj.propaddr else "no property address",
                    '#rentcode#': rentobj.rentcode if rentobj.rentcode else "no rentcode",
                    '#rent_stat#': rent_stat,
                    '#sort_code#': rentobj.sort_code if hasattr(rentobj, 'sort_code') else "no sort_code",
                    '#tenantname#': rentobj.tenantname if rentobj.tenantname else "no tenant name",
                    '#today#': dateToStr(date.today()),
                    }
    rent_strings_3 = {'#charges_list#': charges_list,
                    '#owing_stat#': owing_stat,
                    '#rent_stat#': rent_stat
                    }

    rent_strings_rent = {'charges_list': charges_list,
                           'owing_stat': owing_stat,
                           'rent_stat': rent_stat
                           }
    if type == 'rent':
        return rent_strings_rent
    elif type == 'payrequest':
        return {**rent_strings_1, **rent_strings_2}
    else:
        return {**rent_strings_1, **rent_strings_2, **rent_strings_3}


def get_owing_stat(rentobj, rent_strings):
    if rentobj.statusdet not in ("grouped payment", "sold off", "terminated"):
        totcharges = rentobj.totcharges or 0
        if rentobj.arrears == 0 and totcharges == 0 and rentobj.nextrentdate >= date.today():
            owing_stat = "There is no {0} owing to us on this property and {0} is paid up to {1}. \
                            Further {0} will be due and payable {2} {3} on {4} in the sum of {5}."\
                    .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                            rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears == 0 and totcharges == 0 and rentobj.nextrentdate < date.today():
            owing_stat = "{0} was last paid on this property up to {1}. Further {0} was due and \
                            payable {2} {3} on {4} in the sum of {5} but no rent demand has yet been issued." \
                .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                            rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears > 0 and totcharges == 0 and rentobj.lastrentdate > date.today():
            owing_stat = "A recent pay request has been issued for {} {} due {} {} on {}. \
            This amount is not payable until the date stated on the pay request."\
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#periodly#"],
                            rent_strings["#advarr#"], rent_strings["#nextrentdate#"])
        elif rentobj.arrears > 0 and totcharges == 0 and rentobj.lastrentdate <= date.today():
            owing_stat = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
             to {3}. Further {1} will be due and payable {4} {5} on {6} in the sum of {7}." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears > 0 and totcharges == 0 and rentobj.nextrentdate < date.today():
            owing_stat = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
                             to {3}. Further {1} fell due and payable {4} {5} on {6} in the sum of {7} but no \
                             rent demand has yet been issued." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears == 0 and totcharges > 0 and rentobj.nextrentdate < date.today():
            owing_stat = "The total amount owing to us on this property is {0} as more fully set out below. {1} fell due \
                            and payable {4} {5} on {6} in the sum of {7} but no rent demand has yet been issued." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rentobj.arrears == 0 and totcharges > 0:
            owing_stat = "The total amount owing to us on this property is {0} as more fully set out below. \
                            {1} will next be due and payable {4} {5} on {6} in the sum of {7}." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        else:
            owing_stat = "The total amount owing to us on this property is {0} being {1} {2} owing for the period from {3} \
                             to {4} plus other charges as set out below." \
                .format(rent_strings["#totdue#"], rent_strings["#arrears#"], rent_strings["#rent_type#"],
                        rent_strings["#arrears_start_date#"], rent_strings["#arrears_end_date#"])
        # TODO reduced
    else:
        owing_stat = "no owing statement because the status for this rent is either grouped payment, managed, \
                        sold off or terminated"

    return owing_stat


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


