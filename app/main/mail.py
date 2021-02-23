import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from app.dao.charge import get_rent_charge_details
from app.dao.form_letter import get_form_letter
from app.dao.functions import dateToStr, doReplace, hashCode, moneyToStr
from app.dao.income import get_income_item
from app.dao.lease import get_lease_variables
from app.dao.rent import get_rent_mail


def writeMail(rent_id, form_letter_id, income_id=0):
    rentobj = get_rent_mail(rent_id)
    mail_variables = get_mail_variables(rentobj)
    income_item, allocdata = get_income_item(rent_id, income_id)
    mail_variables['#paidtodate#'] = dateToStr(rentobj.paidtodate) if rentobj else "no paidtodate"
    mail_variables['#payamount#'] = moneyToStr(income_item.payamount, pound=True) if income_item else "no payment"
    mail_variables['#paydate#'] = dateToStr(income_item.paydate) if income_item else "no paydate"
    mail_variables['#payer#'] = income_item.payer if income_item else "no payer"
    mail_variables['#paytypedet#'] = income_item.paytypedet if income_item else "no paytype"
    owing_stat = get_owing_stat(rentobj, mail_variables)
    mail_variables['#owing_stat#'] = owing_stat
    form_letter = get_form_letter(form_letter_id)
    if "LEQ" in form_letter.code:
        leasedata, lease_variables = get_lease_variables(rent_id)
        mail_variables.update(lease_variables)
    else:
        leasedata = None
    subject = form_letter.subject
    block = form_letter.block if form_letter.block else ""
    doctype = form_letter.doctype
    dcode = form_letter.code
    subject = doReplace(mail_variables, subject)
    block = doReplace(mail_variables, block)
    return block, leasedata, rentobj, subject, doctype, dcode


def get_owing_stat(rentobj, mail_variables):
    if rentobj.statusdet in ("sold off", "terminated"):
        owing_stat = "This property has been sold off or terminated and was subject to a {} of {} " \
                     "per annum payable {} {}, last paid to {}."\
                .format(mail_variables["#rent_type#"], mail_variables["#rentpa#"], mail_variables["#periodly#"],
                        mail_variables["#advarr#"], mail_variables["#paidtodate#"])
    elif rentobj.statusdet == "grouped payment":
        owing_stat = "This property is subject to a {} of {} per annum payable {} {} but \
                        this rent is collected within a block rent." \
                .format(mail_variables["#rent_type#"], mail_variables["#rentpa#"], mail_variables["#periodly#"],
                        mail_variables["#advarr#"])
    elif rentobj.arrears == 0 and rentobj.totcharges == 0 and rentobj.nextrentdate >= datetime.date.today():
        owing_stat = "There is no {0} owing to us on this property and {0} is paid up to {1}. \
                        Further {0} will be due and payable {2} {3} on {4} in the sum of {5}."\
                .format(mail_variables["#rent_type#"], mail_variables["#paidtodate#"], mail_variables["#periodly#"],
                        mail_variables["#advarr#"], mail_variables["#nextrentdate#"], mail_variables["#rentgale#"])
    elif rentobj.arrears == 0 and rentobj.totcharges == 0 and rentobj.nextrentdate < datetime.date.today():
        owing_stat = "{0} was last paid on this property up to {1}. Further {0} was due and \
                        payable {2} {3} on {4} in the sum of {5} but no rent demand has yet been issued." \
            .format(mail_variables["#rent_type#"], mail_variables["#paidtodate#"], mail_variables["#periodly#"],
                        mail_variables["#advarr#"], mail_variables["#nextrentdate#"], mail_variables["#rentgale#"])
    elif rentobj.arrears > 0 and rentobj.totcharges == 0 and rentobj.lastrentdate > datetime.date.today():
        owing_stat = "A recent pay request has been issued for {} {} due {} {} on {}. \
        This amount is not payable until the date stated on the pay request."\
            .format(mail_variables["#totdue#"], mail_variables["#rent_type#"], mail_variables["#periodly#"],
                        mail_variables["#advarr#"], mail_variables["#nextrentdate#"])
    elif rentobj.arrears > 0 and rentobj.totcharges == 0 and rentobj.lastrentdate <= datetime.date.today():
        owing_stat = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
         to {3}. Further {1} will be due and payable {4} {5} on {6} in the sum of {7}." \
            .format(mail_variables["#totdue#"], mail_variables["#rent_type#"], mail_variables["#arrears_start_date#"],
                    mail_variables["#arrears_end_date#"], mail_variables["#periodly#"],
                    mail_variables["#advarr#"], mail_variables["#nextrentdate#"], mail_variables["#rentgale#"])
    elif rentobj.arrears > 0 and rentobj.totcharges == 0 and rentobj.nextrentdate < datetime.date.today():
        owing_stat = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
                         to {3}. Further {1} fell due and payable {4} {5} on {6} in the sum of {7} but no \
                         rent demand has yet been issued." \
            .format(mail_variables["#totdue#"], mail_variables["#rent_type#"], mail_variables["#arrears_start_date#"],
                    mail_variables["#arrears_end_date#"], mail_variables["#periodly#"],
                    mail_variables["#advarr#"], mail_variables["#nextrentdate#"], mail_variables["#rentgale#"])
    elif rentobj.arrears == 0 and rentobj.totcharges > 0 and rentobj.nextrentdate < datetime.date.today():
        owing_stat = "The total amount owing to us on this property is {0} as more fully set out below. {1} fell due \
                        and payable {4} {5} on {6} in the sum of {7} but no rent demand has yet been issued." \
            .format(mail_variables["#totdue#"], mail_variables["#rent_type#"], mail_variables["#arrears_start_date#"],
                    mail_variables["#arrears_end_date#"], mail_variables["#periodly#"],
                    mail_variables["#advarr#"], mail_variables["#nextrentdate#"], mail_variables["#rentgale#"])
    elif rentobj.arrears == 0 and rentobj.totcharges > 0:
        owing_stat = "The total amount owing to us on this property is {0} as more fully set out below. \
                        {1} will next be due and payable {4} {5} on {6} in the sum of {7}." \
            .format(mail_variables["#totdue#"], mail_variables["#rent_type#"], mail_variables["#arrears_start_date#"],
                    mail_variables["#arrears_end_date#"], mail_variables["#periodly#"],
                    mail_variables["#advarr#"], mail_variables["#nextrentdate#"], mail_variables["#rentgale#"])
    else:
        owing_stat = "The total amount owing to us on this property is {0} being {1} {2} owing for the period from {3} \
                         to {4} plus other charges as set out below." \
            .format(mail_variables["#totdue#"], mail_variables["#arrears#"], mail_variables["#rent_type#"],
                    mail_variables["#arrears_start_date#"], mail_variables["#arrears_end_date#"])
    # TODO reduced
    if rentobj.totcharges > 0:
        charges = get_rent_charge_details(rentobj.id)
        for charge in charges:
            owing_stat += "\n{} {} added on {}".format(moneyToStr(charge.chargetotal, pound=True),
                             charge.chargedesc, dateToStr(charge.chargestartdate))

    return owing_stat


def get_mail_variables(rentobj):
    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(rentobj.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rentobj.nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(rentobj.lastrentdate)
    rent_gale = (rentobj.rentpa / rentobj.freq_id) if rentobj.rentpa != 0 else 0
    rent_type = "rent charge" if rentobj.tenuredet == "Rentcharge" else "ground rent"
    totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    totdue = arrears + totcharges
    mail_variables = {'#acc_name#': rentobj.acc_name if rentobj.acc_name else "no acc_name",
                    '#acc_num#': rentobj.acc_num if rentobj.acc_num else "no acc_number",
                    '#advarr#': rentobj.advarrdet if rentobj else "no advarr",
                    '#arrears#': moneyToStr(arrears, pound=True),
                    '#arrears_start_date#': arrears_start_date,
                    '#arrears_end_date#': arrears_end_date,
                    '#bank_name#': rentobj.bank_name if rentobj.bank_name else "no bank_name",
                    '#hashcode#': hashCode(rentobj.rentcode) if rentobj else "no hashcode",
                    '#landlord_name#': rentobj.name if rentobj else "no landlord name",
                    '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/1111",
                    '#manageraddr#': rentobj.manageraddr if rentobj else "no manager address",
                    '#manageraddr2#': rentobj.manageraddr2 if rentobj else "no manager address2",
                    '#managername#': rentobj.managername if rentobj else "no manager name",
                    '#nextrentdate#': dateToStr(rentobj.nextrentdate) if rentobj else "no nextrentdate",
                    '#periodly#': rentobj.freqdet if rentobj else "no periodly",
                    '#propaddr#': rentobj.propaddr if rentobj else "no property address",
                    '#rentcode#': rentobj.rentcode if rentobj else "no rentcode",
                    '#rentgale#': moneyToStr(rent_gale, pound=True) if rentobj else "£0.00",
                    '#rentpa#': moneyToStr(rentobj.rentpa, pound=True) if rentobj else "no rent",
                    '#rent_type#': rent_type,
                    '#sort_code#': rentobj.sort_code if rentobj.sort_code else "no sort_code",
                    '#tenantname#': rentobj.tenantname if rentobj else "no tenant name",
                    '#today#': dateToStr(date.today()),
                    '#totcharges#': moneyToStr(totcharges, pound=True),
                    '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due"
                    }
    return mail_variables
