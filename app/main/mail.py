import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from app.dao.form_letter import get_form_letter
from app.dao.functions import dateToStr, doReplace, hashCode, moneyToStr
from app.dao.lease import get_lease_variables
from app.dao.mail import getmaildata
from app.dao.rent_ import get_rent_


def writeMail(rent_id, income_id, form_letter_id, action):
    addressdata, rentobj, word_variables = get_word_variables(rent_id, income_id)
    form_letter = get_form_letter(form_letter_id)
    if action == "lease":
        leasedata, lease_variables = get_lease_variables(rent_id)
        word_variables.update(lease_variables)
    else:
        leasedata = None
    subject = form_letter.subject
    block = form_letter.block if form_letter.block else ""
    doctype = form_letter.desc
    dcode = form_letter.code
    subject = doReplace(word_variables, subject)
    block = doReplace(word_variables, block)
    return addressdata, block, leasedata, rentobj, subject, doctype, dcode


def get_owing_stat(rentobj, word_variables):
    if rentobj.statusdet in ("sold off", "terminated"):
        owing_stat = "This property has been sold off or terminated and was subject to a {} of {} " \
                     "per annum payable {} {}, last paid to {}."\
                .format(word_variables["#rent_type#"], word_variables["#rentpa#"], word_variables["#periodly#"],
                        word_variables["#advarr#"], word_variables["#paidtodate#"])
    elif rentobj.statusdet == "grouped payment":
        owing_stat = "This property is subject to a {} of {} per annum payable {} {} but \
                        this rent is collected within a block rent." \
                .format(word_variables["#rent_type#"], word_variables["#rentpa#"], word_variables["#periodly#"],
                        word_variables["#advarr#"])
    elif rentobj.arrears == 0 and rentobj.totcharges == 0 and rentobj.nextrentdate >= datetime.date.today():
        owing_stat = "There is no {0} owing to us on this property and {0} is paid up to {1}. \
                        Further {0} will be due and payable {2} {3} on {4} in the sum of {5}."\
                .format(word_variables["#rent_type#"], word_variables["#paidtodate#"], word_variables["#periodly#"],
                        word_variables["#advarr#"], word_variables["#nextrentdate#"], word_variables["#rentgale#"])
    elif rentobj.arrears == 0 and rentobj.totcharges == 0 and rentobj.nextrentdate <= datetime.date.today():
        owing_stat = "{0} was last paid on this property up to {1}. Further {0} was due and \
                        payable {2} {3} on {4} in the sum of {5} but no rent demand has yet been issued." \
            .format(word_variables["#rent_type#"], word_variables["#paidtodate#"], word_variables["#periodly#"],
                        word_variables["#advarr#"], word_variables["#nextrentdate#"], word_variables["#rentgale#"])
    elif rentobj.arrears > 0 and rentobj.totcharges == 0 and rentobj.lastrentdate > datetime.date.today():
        owing_stat = "A recent pay request has been issued showing the total amount owing to us on this property \
        as {} being {} owing for the period {}. This amount is not payable until the date stated on the pay request."\
            .format(word_variables["#totdue#"], word_variables["#rent_type#"], word_variables["#periodly#"],
                        word_variables["#advarr#"], word_variables["#nextrentdate#"], word_variables["#rentgale#"])
    elif rentobj.arrears > 0 and rentobj.totcharges == 0 and \
        rentobj.lastrentdate <= datetime.date.today() < rentobj.nextrentdate:
        owing_stat = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
         to {3}. Further {1} will be due and payable {4} {5} on {6} in the sum of {7}." \
            .format(word_variables["#totdue#"], word_variables["#rent_type#"], word_variables["#arrears_start_date#"],
                    word_variables["#arrears_end_date#"], word_variables["#periodly#"],
                    word_variables["#advarr#"], word_variables["#nextrentdate#"], word_variables["#rentgale#"])
    elif rentobj.arrears > 0 and rentobj.totcharges == 0 and \
             rentobj.nextrentdate < datetime.date.today():
        owing_stat = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
                         to {3}. Further {1} will be due and payable {4} {5} on {6} in the sum of {7} but no \
                         rent demand has yet been issued." \
            .format(word_variables["#totdue#"], word_variables["#rent_type#"], word_variables["#arrears_start_date#"],
                    word_variables["#arrears_end_date#"], word_variables["#periodly#"],
                    word_variables["#advarr#"], word_variables["#nextrentdate#"], word_variables["#rentgale#"])
    # TODO several more cases for Hez to deal with here - particularly where charges are owing as well as rent and also
    # TODO reduced rents
    else:
        owing_stat = "owing stat not yet deduced for this case: Please see Hez"
    return owing_stat

def get_word_variables(rent_id, income_id=0):
    rentobj = get_rent_(rent_id)
    incomedata, allocdata, bankdata, addressdata = getmaildata(rent_id, income_id)

    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(rentobj.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rentobj.nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(rentobj.lastrentdate)
    rent_gale = (rentobj.rentpa / rentobj.freq_id) if rentobj.rentpa != 0 else 0
    # TODO: Check if rentobj.tenuredet == "Rentcharge" below

    rent_type = "rent charge" if rentobj.tenuredet == "Rentcharge" else "ground rent"
    totcharges = rentobj.totcharges if rentobj.totcharges else Decimal(0)
    totdue = arrears + totcharges
    word_variables = {'#advarr#': rentobj.advarrdet if rentobj else "no advarr",
                      '#acc_name#': bankdata.acc_name if bankdata else "no acc_name",
                      '#acc_num#': bankdata.acc_num if bankdata else "no acc_number",
                      '#sort_code#': bankdata.sort_code if bankdata else "no sort_code",
                      '#bank_name#': bankdata.bank_name if bankdata else "no bank_name",
                      '#arrears#': moneyToStr(arrears, pound=True),
                      '#hashcode#': hashCode(rentobj.rentcode) if rentobj else "no hashcode",
                      '#address#': addressdata.address if addressdata else "no landlord address",
                      '#landlord_name#': rentobj.name if rentobj else "no landlord name",
                      '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/1111",
                      '#lessor#': "rent charge owner" if rentobj.tenuredet == "Rentcharge" else "ground rent owner",
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
                      '#rentgale#': moneyToStr(rent_gale, pound=True) if rentobj else "£0.00",
                      '#rentpa#': moneyToStr(rentobj.rentpa, pound=True) if rentobj else "no rent",
                      '#rent_type#': rent_type,
                      '#tenantname#': rentobj.tenantname if rentobj else "no tenant name",
                      '#totcharges#': moneyToStr(totcharges, pound=True),
                      '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due",
                      '#today#': dateToStr(datetime.date.today())
                      }
    owing_stat = get_owing_stat(rentobj, word_variables)
    word_variables['owing_stat'] = owing_stat
    return addressdata, rentobj, word_variables