from flask import request
from app.main.form_letter import mget_form_letter
from app.dao.income import get_income_item
from app.dao.rent import get_rent_md
from app.main.functions import dateToStr, doReplace, moneyToStr
from app.main.lease import mget_lease_variables
from app.main.rent import get_mailaddr, get_propaddr, get_rentp, get_rent_strings
from app.modeltypes import PayTypes


def get_mail_pack(rent_id):    # get small collection of variables for mail dialog
    rent = get_rent_md(rent_id)    # get minimal Rent variables for mail dialog
    mail_pack = {'rent_id': rent_id, 'rentcode': rent.rentcode}
    mail_pack['mailaddr'] = get_mailaddr(rent_id, rent.agent_id, rent.mailto_id, rent.tenantname)
    mail_pack['propaddr'] = get_propaddr(rent_id)
    mail_pack['tenantname'] = rent.tenantname
    return mail_pack


def writeMail(form_letter_id, template):
    income_id = request.form.get('income_id') or 0
    rent_id = int(request.form.get('rent_id'))
    rent = get_rentp(rent_id)    # get full enhanced rent pack
    variables = get_rent_strings(rent, 'mail') if template == 'LTS' else get_rent_strings(rent, 'xray')
    income_item, allocdata = get_income_item(rent_id, income_id)
    variables['#payamount#'] = moneyToStr(income_item.payamount, pound=True) if income_item else "no payment"
    variables['#paydate#'] = dateToStr(income_item.paydate) if income_item else "no paydate"
    variables['#payer#'] = income_item.payer if income_item else "no payer"
    variables['#paytypedet#'] = PayTypes.get_name(income_item.paytype_id) if income_item else "no paytype"
    form_letter = mget_form_letter(form_letter_id)
    leasedata = None
    if "LEQ" in form_letter.code:
        leasedata, lease_variables = mget_lease_variables(rent_id)
        variables.update(lease_variables)
    block = form_letter.block if form_letter.block else ""
    doctype_id = form_letter.doctype_id
    subject = doReplace(variables, form_letter.subject)
    if template == 'LTS':
        block = doReplace(variables, block)
    return block, doctype_id, leasedata, rent, subject, variables

