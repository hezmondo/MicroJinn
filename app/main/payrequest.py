import json
from app import decimal_default
from datetime import date, timedelta
from decimal import Decimal
from flask import request
from dateutil.relativedelta import relativedelta
from app.dao.form_letter import get_email_form_by_code, get_pr_form
from app.dao.functions import commit_to_database, dateToStr, doReplace, moneyToStr
from app.dao.payrequest import add_pr_history, get_recovery_info, \
    prepare_new_pr_history_entry
from app.dao.charge import add_charge, get_charge_start_date, get_charge_type, get_rent_charge_details
from app.dao.rent import get_rent, get_rent_mail, update_roll_rent
from app.main.mail import get_mail_variables
from app.dao.case import merge_case
from app.dao.doc_ import convert_html_to_pdf


def build_arrears_statement(rent_type, arrears_start_date, arrears_end_date):
    statement = "Unpaid {0} is owing for the period {1} to {2}:".format(rent_type, arrears_start_date, arrears_end_date)
    return statement


def build_charges_suffix(rent_mail):
    periods = calculate_periods(rent_mail.arrears, rent_mail.freq_id, rent_mail.rentpa)
    charges_total = rent_mail.totcharges if rent_mail.totcharges else 0
    pr_exists = True if rent_mail.prexists == 1 else False
    last_arrears_level = rent_mail.lastarrearslevel if pr_exists else ""
    charge_start_date = get_charge_start_date(rent_mail.id)
    charge_90_days = charge_start_date and date.today() - charge_start_date > timedelta(90)
    return build_charges_suffix_string(periods, charges_total, pr_exists, last_arrears_level, charge_90_days)


def build_charges_suffix_string(periods, charges_total, pr_exists, last_arrears_level, charge_90_days):
    if periods == 0 and charges_total > 0 and charge_90_days:
        return "ZERACH"
    elif periods == 0:
        return "ZERA"
    elif periods > 0 and last_arrears_level == ArrearsLevel.Normal and not pr_exists:
        return "ZERA"
    elif periods > 0 and last_arrears_level == ArrearsLevel.Normal and pr_exists:
        return "ARW"
    elif periods > 1 and last_arrears_level == ArrearsLevel.Warning:
        return "ARC1"
    elif periods > 1 and last_arrears_level == ArrearsLevel.First:
        return "ARC2"
    elif periods > 2 and last_arrears_level == ArrearsLevel.Second:
        return "ARC3"
    elif periods > 3 and last_arrears_level == ArrearsLevel.Third:
        return "ARC4"
    # TODO: Check what we want to do when last_arrears_level = 4. Jinn reverts back to warning.
    else:
        return "ARW"


def build_new_arrears_level_string(suffix):
    if suffix == "ZERA" or suffix == "ZERACH":
        return ArrearsLevel.Normal
    elif suffix == "ARW":
        return ArrearsLevel.Warning
    elif suffix == "ARC1":
        return ArrearsLevel.First
    elif suffix == "ARC2":
        return ArrearsLevel.Second
    elif suffix == "ARC3":
        return ArrearsLevel.Third
    elif suffix == "ARC4":
        return ArrearsLevel.Fourth


def build_pr_charges_table(rent_mail):
    charges = get_rent_charge_details(rent_mail.id)
    charge_table_items = {}
    new_charge_dict = {}
    total_charges = 0
    for charge in charges:
        charge_details = "{} added on {}:".format(charge.chargedesc.capitalize(), dateToStr(charge.chargestartdate))
        charge_total = charge.chargetotal
        charge_table_items.update({charge_details: moneyToStr(charge_total, pound=True)})
        total_charges = total_charges + charge_total
    suffix = build_charges_suffix(rent_mail)
    arrears_clause, create_case, recovery_charge_amount = get_recovery_info(suffix)
    new_arrears_level = build_new_arrears_level_string(suffix)
    if recovery_charge_amount > 0 and not check_recovery_in_charges(charges, recovery_charge_amount):
        charge_details = "{} added on {}:".format("Recovery costs", dateToStr(date.today()))
        charge_table_items.update({charge_details: moneyToStr(recovery_charge_amount, pound=True)})
        total_charges = total_charges + recovery_charge_amount
        new_charge_dict = {
            'rent_id': rent_mail.id,
            'charge_total': recovery_charge_amount,
            'charge_type_id': 10
        }
    return arrears_clause, charge_table_items, create_case, total_charges, new_charge_dict, new_arrears_level


def build_pr_table(rent_mail, pr_variables):
    rent_gale = (rent_mail.rentpa / rent_mail.freq_id) if rent_mail.rentpa != 0 else 0
    arrears = rent_mail.arrears
    arrears_start_date = pr_variables.get('#arrears_start_date#')
    arrears_end_date = pr_variables.get('#arrears_end_date#')
    rent_type = pr_variables.get('#rent_type#')
    table_rows = {}
    if rent_gale:
        rent_statement = build_rent_statement(rent_mail, rent_type)
        table_rows.update({rent_statement: moneyToStr(rent_gale, pound=True)})
    if arrears:
        arrears_statement = build_arrears_statement(rent_type, arrears_start_date, arrears_end_date)
        table_rows.update({arrears_statement: moneyToStr(arrears, pound=True)})
    arrears_clause, charge_table_items, create_case, total_charges, \
        new_charge_dict, new_arrears_level = build_pr_charges_table(rent_mail)
    if total_charges:
        table_rows.update(charge_table_items)
    totdue = rent_gale + arrears + total_charges
    return arrears_clause, create_case, new_arrears_level, new_charge_dict, rent_type, table_rows, totdue


def build_rent_statement(rent_mail, rent_type):
    statement = "{0} {1} due and payable {2} on {3}:".format(rent_mail.freqdet, rent_type, rent_mail.advarrdet,
                                                                 dateToStr(rent_mail.nextrentdate))
    statement = statement[0].upper() + statement[1:]
    return statement


def calculate_periods(arrears, freq_id, rent_pa):
    return arrears * freq_id / rent_pa


def check_recovery_in_charges(charges, recovery_charge_amount):
    includes_recovery = False
    for charge in charges:
        if charge.chargetotal == recovery_charge_amount and charge.chargedesc == "recovery costs":
            includes_recovery = True
    return includes_recovery


def create_case(rent_id, pr_id):
    case_details = "Automatically created by payrequest {} on {}".format(pr_id, dateToStr(date.today()))
    case_nad = date.today() + relativedelta(days=30)
    merge_case(case_details, case_nad, rent_id)


def forward_rent(rent_id):
    rent = get_rent(rent_id)
    arrears = rent.arrears + (rent.rentpa / rent.freq_id)
    update_roll_rent(rent_id, arrears)
    # if not from_batch:
    # else:
    #     return dict(id=rent_id, lastrentdate=last_rent_date, arrears=arrears)


def forward_rent_case_and_charges(pr_history, pr_save_data, rent_id):
    forward_rent(rent_id)
    new_charge_dict = pr_save_data.get("new_charge_dict")
    if len(new_charge_dict) > 0:
        save_charge(new_charge_dict.get("rent_id"), Decimal(new_charge_dict.get("charge_total")),
                   new_charge_dict.get("charge_type_id"))
    if pr_save_data.get("create_case"):
        create_case(rent_id, pr_history.id)
    return pr_history.id


def save_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(date.today())
    charge_type = get_charge_type(chargetype_id)
    charge_details = "£{} {} added on {}".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    add_charge(rent_id, recovery_charge_amount, chargetype_id, charge_details)


def save_new_payrequest(method):
    block, pr_save_data, pr_history, rent_id = save_new_pr_history_entry(method)
    if method != 'email':
        convert_html_to_pdf(block, 'pr.pdf')
    add_pr_history(pr_history)
    pr_id = forward_rent_case_and_charges(pr_history, pr_save_data, rent_id)
    commit_to_database()
    return pr_id, pr_save_data, rent_id


def save_new_pr_history_entry(method):
    block = request.form.get('xinput').replace("£", "&pound;")
    pr_save_data = json.loads(request.form.get('pr_save_data'))
    rent_id = request.args.get('rent_id', type=int)
    mailaddr = request.form.get('pr_addr')
    pr_history = prepare_new_pr_history_entry(block, pr_save_data, rent_id, mailaddr, method)
    return block, pr_save_data, pr_history, rent_id


def serialize_pr_save_data(pr_save_data):
    pr_save_data = json.dumps(pr_save_data, default=decimal_default)
    return pr_save_data


def write_payrequest(rent_id, pr_form_id):
    rent_mail = get_rent_mail(rent_id)
    pr_variables = get_mail_variables(rent_mail)
    arrears_clause, create_case, new_arrears_level, new_charge_dict, rent_type, table_rows, totdue = \
        build_pr_table(rent_mail, pr_variables)
    totdue_string = moneyToStr(totdue, pound=True) if totdue else "no total due"
    pr_variables.update({'#totdue#': totdue_string})
    subject = "{} account for property: #propaddr#".format(rent_type.capitalize())
    subject = doReplace(pr_variables, subject)
    pr_form = get_pr_form(pr_form_id)
    arrears_clause = doReplace(pr_variables, arrears_clause) + '\n\n' if arrears_clause else ""
    block = arrears_clause.capitalize() + doReplace(pr_variables, pr_form.block) if pr_form.block else ""
    # TODO: pr_save_data can be cleaned up if we are passing all pr_variables in the dictionary
    pr_save_data = {
        'create_case': create_case,
        'new_arrears_level': new_arrears_level,
        'new_charge_dict': new_charge_dict,
        'pr_code': pr_form.code,
        'rent_date_string': str(rent_mail.nextrentdate),
        'tot_due': totdue,
        'pr_variables': pr_variables
    }
    return block, pr_save_data, rent_mail, subject, table_rows, totdue_string


def write_payrequest_email(pr_save_data):
    # TODO: Currently hardcoded access to email form EPR in letter_form - change if users can save and use their
    #  own templates
    email_form = get_email_form_by_code('EPR')
    email_block = doReplace(pr_save_data.get('pr_variables'), email_form.block)
    return email_block


class ArrearsLevel:
    Normal = ""
    Warning = "W"
    First = "1"
    Second = "2"
    Third = "3"
    Fourth = "4"