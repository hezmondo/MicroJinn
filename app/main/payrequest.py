import json
from app import decimal_default
from datetime import date, timedelta
from app.dao.form_letter import get_pr_form
from app.dao.functions import dateToStr, doReplace, moneyToStr
from app.dao.payrequest import get_charge_start_date, get_email_form_by_code, get_recovery_info, get_rent_charge_details
from app.dao.rent import get_rent_mail
from app.main.mail import get_mail_variables


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