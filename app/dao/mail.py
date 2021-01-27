import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from sqlalchemy import desc
from app.models import Income, Incomealloc, Landlord, Manager, Money_account, Rent, Typepayment
from app.dao.form_letter import get_formletter, get_formpayrequest
from app.dao.functions import dateToStr, hashCode, moneyToStr
from app.dao.lease import get_lease_variables
from app.dao.payrequest_ import get_rent_pr, get_rent_statement, get_arrears_statement, get_pr_form, get_pr_variables
from app.dao.rent_ import get_rent_
from app.views.payrequest_ import create_pr_charges_table


# mail
def getmaildata(rent_id, income_id=0):
    if income_id == 0:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                                                                                    Income.date.label("paydate"),
                                                                                    Income.amount.label("payamount"),
                                                                                    Typepayment.paytypedet) \
            .filter(Incomealloc.rent_id == rent_id).order_by(desc(Income.date)).limit(1).one_or_none()
        # income_id = incomedata.id
    else:
        incomedata = Income.query.join(Incomealloc).join(Typepayment).with_entities(Income.id, Income.payer,
                                                                                    Income.date.label("paydate"),
                                                                                    Income.amount.label("payamount"),
                                                                                    Typepayment.paytypedet) \
            .filter(Income.id == income_id).first()
    # allocdata = Incomealloc.join(Chargetype).with_entities(Incomealloc.id, Incomealloc.income_id,
    #                     Incomealloc.rentcode, Incomealloc.amount.label("alloctot"),
    #                     Chargetype.chargedesc).filter(Incomealloc.income_id == income_id).all()
    allocdata = None
    bankdata = Money_account.query.join(Landlord).join(Rent).with_entities(Money_account.acc_name, Money_account.acc_num,
                                                                           Money_account.sort_code,
                                                                           Money_account.bank_name).filter(
        Rent.id == rent_id) \
        .one_or_none()
    addressdata = Landlord.query.join(Rent).join(Manager).with_entities(
        Landlord.landlordaddr, Manager.manageraddr, Manager.manageraddr2,
    ).filter(Rent.id == rent_id).one_or_none()

    return incomedata, allocdata, bankdata, addressdata


def writeMail(rent_id, income_id, formletter_id, action):
    addressdata, rentobj, word_variables = get_word_variables(rent_id, income_id)
    formletter = get_formletter(formletter_id)

    if action == "lease":
        leasedata, lease_variables = get_lease_variables(rent_id)
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


def write_payrequest(rent_id, pr_form_id):
    rent_pr = get_rent_pr(rent_id)
    pr_variables = get_pr_variables(rent_pr)
    rent_gale = (rent_pr.rentpa / rent_pr.freq_id) if rent_pr.rentpa != 0 else 0
    arrears = rent_pr.arrears
    arrears_start_date = pr_variables.get('#arrears_start_date#')
    arrears_end_date = pr_variables.get('#arrears_end_date#')
    rent_type = pr_variables.get('#rent_type#')

    table_rows = {}
    if rent_gale:
        rent_statement = get_rent_statement(rent_pr, rent_type)
        table_rows.update({rent_statement: moneyToStr(rent_gale, pound=True)})
    if arrears:
        arrears_statement = get_arrears_statement(rent_type, arrears_start_date, arrears_end_date)
        table_rows.update({arrears_statement: moneyToStr(arrears, pound=True)})
    arrears_clause, charge_table_items, create_case, total_charges, \
        new_charge_dict, new_arrears_level = create_pr_charges_table(rent_pr)
    if total_charges:
        table_rows.update(charge_table_items)
    totdue = rent_gale + arrears + total_charges

    totdue_string = moneyToStr(totdue, pound=True) if totdue else "no total due"

    pr_variables.update({'#totdue#': totdue_string})

    subject = "{} account for property: #propaddr#".format(rent_type.capitalize())
    subject = doReplace(pr_variables, subject)

    pr_form = get_pr_form(pr_form_id)
    pr_code = pr_form.code

    arrears_clause = doReplace(pr_variables, arrears_clause) + '\n\n' if arrears_clause else ""
    block = arrears_clause.capitalize() + doReplace(pr_variables, pr_form.block) if pr_form.block else ""

    pr_data = {
        'create_case': create_case,
        'new_arrears_level': new_arrears_level,
        'new_charge_dict': new_charge_dict,
        'pr_code': pr_code,
        'rent_date_string': str(rent_pr.nextrentdate),
        'rent_id': rent_id,
        'rentcode': rent_pr.rentcode,
        'subject': subject,
        'tot_due': totdue
    }

    return block, pr_data, rent_pr, table_rows, totdue_string


def doReplace(dict, clause):
    for key, value in dict.items():
        clause = clause.replace(key, value)

    return clause


def get_word_variables(rent_id, income_id=0):
    rentobj = get_rent_(rent_id)
    incomedata, allocdata, bankdata, addressdata = getmaildata(rent_id, income_id)

    arrears = rentobj.arrears if rentobj.arrears else Decimal(0)
    arrears_start_date = dateToStr(rentobj.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rentobj.nextrentdate + relativedelta(days=-1)) \
        if rentobj.advarrdet == "in advance" else dateToStr(rentobj.lastrentdate)
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
                      '#landlordaddr#': addressdata.landlordaddr if addressdata else "no landlord address",
                      '#landlordname#': rentobj.landlordname if rentobj else "no landlord name",
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
                      '#rentpa#': moneyToStr(rentobj.rentpa, pound=True) if rentobj else "no rent",
                      '#rent_type#': rent_type,
                      '#tenantname#': rentobj.tenantname if rentobj else "no tenant name",
                      '#totcharges#': moneyToStr(totcharges, pound=True),
                      '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due",
                      '#today#': dateToStr(datetime.date.today())
                      }

    return addressdata, rentobj, word_variables