from app.dao.form_letter import get_form_letter
from app.main.functions import dateToStr, doReplace, moneyToStr
from app.dao.income import get_income_item
from app.dao.lease import get_lease_variables
from app.dao.rent import get_rent_mail
from app.main.rent import get_rent_strings


def writeMail(rent_id, form_letter_id, income_id=0):
    rentobj = get_rent_mail(rent_id)
    mail_variables = get_rent_strings(rentobj, 'mail')
    income_item, allocdata = get_income_item(rent_id, income_id)
    mail_variables['#payamount#'] = moneyToStr(income_item.payamount, pound=True) if income_item else "no payment"
    mail_variables['#paydate#'] = dateToStr(income_item.paydate) if income_item else "no paydate"
    mail_variables['#payer#'] = income_item.payer if income_item else "no payer"
    mail_variables['#paytypedet#'] = income_item.paytypedet if income_item else "no paytype"
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


def writeMail_xray(rent_id, form_letter_id, income_id=0):
    rentobj = get_rent_mail(rent_id)
    variables = get_rent_strings(rentobj, 'xray')
    income_item, allocdata = get_income_item(rent_id, income_id)
    variables['payamount'] = moneyToStr(income_item.payamount, pound=True) if income_item else "no payment"
    variables['paydate'] = dateToStr(income_item.paydate) if income_item else "no paydate"
    variables['payer'] = income_item.payer if income_item else "no payer"
    variables['paytypedet'] = income_item.paytypedet if income_item else "no paytype"
    form_letter = get_form_letter(form_letter_id)
    if "LEQ" in form_letter.code:
        leasedata, lease_variables = get_lease_variables(rent_id)
        variables.update(lease_variables)
    else:
        leasedata = None

    return leasedata, rentobj, variables
