import datetime
import json
from app import decimal_default
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import request
from dateutil.relativedelta import relativedelta
from app.dao.action import add_action
from app.dao.case import check_case_exists, add_case
from app.dao.charge import add_charge, get_charge_type, get_total_charges
from app.dao.database import commit_to_database
from app.dao.doc import convert_html_to_pdf
from app.dao.form_letter import get_email_form_by_code, get_pr_form
from app.dao.payrequest import add_pr_history, get_last_arrears_level, get_pr_charge, get_pr_file, get_pr_history_row, \
    get_recovery_info, get_recovery_info_x, prepare_new_pr_history_entry, prepare_new_pr_history_entry_x, \
    post_updated_payrequest_delivery, add_pr_charge
from app.dao.common import delete_record_basic
from app.main.functions import dateToStr, doReplace, moneyToStr
from app.main.rent import get_rent_gale, get_rentp, get_rent_strings, update_roll_rent, update_rollback_rent
from app.main.common import inc_date_m


def append_pr_date_variables(rent_pr):
    rent_pr.arrears_start_date = rent_pr.paidtodate + relativedelta(days=1)
    rent_pr.arrears_end_date = rent_pr.nextrentdate + relativedelta(days=-1)
    rent_pr.pay_date = date.today() + relativedelta(days=30)
    rent_pr.next_gale_start = rent_pr.nextrentdate if rent_pr.advarrdet == "in advance" else \
        rent_pr.lastrentdate + relativedelta(days=1)
    rent_pr.arrears_end_date_1 = inc_date_m(rent_pr.lastrentdate, rent_pr.freq_id, rent_pr.datecode_id,
                                            2) + relativedelta(
        days=-1) if rent_pr.advarrdet == "in advance" else rent_pr.nextrentdate
    return rent_pr


def append_pr_history_details(rent_pr):
    rent_pr.pr_exists = False
    rent_pr.last_arrears_level = ''
    last_arrears_level_row = get_last_arrears_level(rent_pr.id)
    if last_arrears_level_row:
        rent_pr.pr_exists = True
        rent_pr.last_arrears_level = last_arrears_level_row[0]
    return rent_pr


def build_arrears_statement(rent_type, arrears_start_date, arrears_end_date):
    statement = "Unpaid {0} is owing for the period {1} to {2}:".format(rent_type, arrears_start_date, arrears_end_date)
    return statement


def build_charges_suffix(rent_pr):
    periods = calculate_periods(rent_pr.arrears, rent_pr.freq_id, rent_pr.rentpa)
    charges_total = rent_pr.totcharges if rent_pr.totcharges else 0
    charge_start_date = mget_recent_charge_date(rent_pr) if rent_pr.totcharges else False
    charge_90_days = charge_start_date and date.today() - charge_start_date > timedelta(90)
    return build_charges_suffix_string(periods, charges_total, rent_pr.pr_exists, rent_pr.last_arrears_level,
                                       charge_90_days)


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


def build_pr_charges_table(rent_pr):
    charge_table_items = {}
    new_charge_dict = {}
    for charge in rent_pr.charges:
        charge_details = "{} added on {}:".format(charge.chargetype.chargedesc.capitalize(),
                                                  dateToStr(charge.chargestartdate))
        charge_table_items.update({charge_details: moneyToStr(charge.chargetotal, pound=True)})
    suffix = build_charges_suffix(rent_pr)
    arrears_clause, create_case, recovery_charge_amount = get_recovery_info(suffix)
    new_arrears_level = build_new_arrears_level_string(suffix)
    if recovery_charge_amount > 0 and not check_recovery_in_charges(rent_pr.charges, recovery_charge_amount):
        charge_details = "{} added on {}:".format("Recovery costs", dateToStr(date.today()))
        charge_table_items.update({charge_details: moneyToStr(recovery_charge_amount, pound=True)})
        rent_pr.totcharges = rent_pr.totcharges + recovery_charge_amount
        new_charge_dict = {
            'rent_id': rent_pr.id,
            'charge_total': recovery_charge_amount,
            'charge_type_id': 10
        }
    return arrears_clause, charge_table_items, create_case, new_charge_dict, new_arrears_level


def build_pr_table(rent_pr, pr_variables):
    arrears_start_date = pr_variables.get('#arrears_start_date#')
    arrears_end_date = pr_variables.get('#arrears_end_date#')
    table_rows = {}
    if rent_pr.rent_gale:
        rent_statement = build_rent_statement(rent_pr)
        table_rows.update({rent_statement: moneyToStr(rent_pr.rent_gale, pound=True)})
    if rent_pr.arrears:
        arrears_statement = build_arrears_statement(rent_pr.rent_type, arrears_start_date, arrears_end_date)
        table_rows.update({arrears_statement: moneyToStr(rent_pr.arrears, pound=True)})
    arrears_clause, charge_table_items, create_case, \
    new_charge_dict, new_arrears_level = build_pr_charges_table(rent_pr)
    if rent_pr.totcharges:
        table_rows.update(charge_table_items)
    totdue = rent_pr.rent_gale + rent_pr.arrears + rent_pr.totcharges
    new_arrears = rent_pr.arrears + rent_pr.rent_gale
    return arrears_clause, create_case, new_arrears, new_arrears_level, new_charge_dict, table_rows, totdue


def build_rent_statement(rent_pr):
    statement = "{0} {1} due and payable {2} on {3}:".format(rent_pr.freqdet, rent_pr.rent_type, rent_pr.advarrdet,
                                                             dateToStr(rent_pr.nextrentdate))
    statement = statement[0].upper() + statement[1:]
    return statement


def calculate_periods(arrears, freq_id, rent_pa):
    return round(arrears * freq_id / rent_pa) if rent_pa != 0 else 0


def check_recovery_in_charges(charges, recovery_charge_amount):
    includes_recovery = False
    for charge in charges:
        if charge.chargetotal == recovery_charge_amount and charge.chargetype.chargedesc == "recovery costs":
            includes_recovery = True
    return includes_recovery


def collect_pr_history_data():
    return {'block': request.form.get('xinput'),
            'mailaddr': request.form.get('pr_addr'),
            'pr_code': request.form.get('pr_code'),
            'rent_date': request.form.get('rent_date'),
            'tot_due': request.form.get('tot_due'),
            'new_arrears_level': request.form.get('new_arrears_level'),
            'new_arrears': request.form.get('new_arrears'),
            'charge_total': request.form.get('charge_total')}


def collect_pr_rent_data():
    return {'rent_date': request.form.get('rent_date'),
            'new_arrears': request.form.get('new_arrears'),
            'charge_total': request.form.get('charge_total')}


def create_case(rent_id, pr_id):
    case_details = "Automatically created by payrequest {} on {}".format(pr_id, dateToStr(date.today()))
    case_nad = date.today() + relativedelta(days=30)
    add_case(case_details, case_nad, rent_id)


def create_new_pr_history_entry(method):
    block = request.form.get('xinput').replace("£", "&pound;")
    pr_save_data = json.loads(request.form.get('pr_save_data'))
    rent_id = request.args.get('rent_id', type=int)
    mailaddr = request.form.get('pr_addr')
    pr_history = prepare_new_pr_history_entry(block, pr_save_data, rent_id, mailaddr, method)
    return block, pr_save_data, pr_history, rent_id


# def forward_rent(rent_id):
#     rent = get_rentp(rent_id)
#     arrears = rent.arrears + (rent.rentpa / rent.freq_id)
#     update_roll_rent(rent_id, arrears)
# if not from_batch:
# else:
#     return dict(id=rent_id, lastrentdate=last_rent_date, arrears=arrears)


def forward_rent_case_and_charges(pr_id, pr_save_data, rent_id):
    last_rent_date = datetime.strptime(pr_save_data.get('rent_date_string'), '%d-%b-%Y').date()
    arrears = pr_save_data.get('new_arrears')
    update_roll_rent(rent_id, last_rent_date, arrears)
    new_charge_dict = pr_save_data.get("new_charge_dict")
    charge_id = None
    case_created = False
    if len(new_charge_dict) > 0:
        charge_id = save_charge(new_charge_dict.get("rent_id"), Decimal(new_charge_dict.get("charge_total")),
                                new_charge_dict.get("charge_type_id"))
    if not check_case_exists(rent_id):
        create_case(rent_id, pr_id)
        case_created = True
    return case_created, charge_id


def forward_rent_case_and_charges_x(pr_id, pr_rent_data, rent_id):
    last_rent_date = datetime.strptime(pr_rent_data.get('rent_date'), '%Y-%m-%d').date()
    update_roll_rent(rent_id, last_rent_date, pr_rent_data.get('new_arrears'))
    charge_id = None
    case_created = False
    if Decimal(pr_rent_data.get('charge_total')) > 0:
        charge_id = save_charge(rent_id, Decimal(pr_rent_data.get('charge_total')), 10)
    if not check_case_exists(rent_id):
        create_case(rent_id, pr_id)
        case_created = True
    return case_created, charge_id


def mget_recent_charge_date(rent_pr):
    charge_start_dates = []
    for charge in rent_pr.charges:
        charge_start_dates.append(charge.chargestartdate)
    return max(charge_start_dates)


def save_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(date.today())
    charge_type = get_charge_type(chargetype_id)
    charge_details = "£{} {} added on {}".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    charge_id = add_charge(rent_id, recovery_charge_amount, chargetype_id, charge_details)
    return charge_id


def save_new_payrequest(method):
    block, pr_save_data, pr_history, rent_id = create_new_pr_history_entry(method)
    if method != 'email':
        convert_html_to_pdf(block, 'pr.pdf')
    pr_id = add_pr_history(pr_history)
    case_created, charge_id = forward_rent_case_and_charges(pr_id, pr_save_data, rent_id)
    if charge_id or case_created:
        add_pr_charge(pr_id, charge_id, case_created)
    commit_to_database()
    return pr_id, pr_save_data, rent_id


def save_new_payrequest_x(method, pr_history_data, pr_rent_data, rent_id):
    pr_history = prepare_new_pr_history_entry_x(pr_history_data, rent_id, method)
    # make a pdf to post or send as an attachment
    convert_html_to_pdf(pr_history_data.get('block'), 'pr.pdf')
    pr_id = add_pr_history(pr_history)
    case_created, charge_id = forward_rent_case_and_charges_x(pr_id, pr_rent_data, rent_id)
    if charge_id or case_created:
        add_pr_charge(pr_id, charge_id, case_created)
    # save action to actions table
    action_str = 'Pay request for rent ' + str(rent_id) + ' totalling ' + str(pr_history_data.get('tot_due')) + ' saved'
    add_action(2, 0, action_str, 'pr_bp.pr_history', {'rent_id': rent_id})
    commit_to_database()
    return pr_id


def serialize_pr_save_data(pr_save_data):
    pr_save_data = json.dumps(pr_save_data, default=decimal_default)
    return pr_save_data


def undo_pr(pr_id):
    pr_file = get_pr_file(pr_id)
    rent_id = pr_file.rent_id
    try:
        rentobj = get_rentp(rent_id)  # get full enhanced rent pack
        if pr_file.rent_date != rentobj.lastrentdate:
            message = "Cannot complete undo. The pay request rent date is not the same as the rent's last rent date."
            return message, rent_id
        charges = get_total_charges(rent_id)
        tot_charges = 0
        for charge in charges:
            tot_charges += charge.chargetotal
        if pr_file.total_due != rentobj.arrears + tot_charges:
            message = "Cannot complete undo. Rent arrears or charges have been altered."
            return message, rent_id
        pr_charge = get_pr_charge(pr_id)
        if pr_charge:
            delete_record_basic(pr_id, 'pr_charge')
            if pr_charge.charge_id:
                delete_record_basic(pr_charge.charge_id, 'charge')
            if pr_charge.case_created:
                delete_record_basic(rent_id, 'case')
        delete_record_basic(pr_id, 'pr_file')
        rent_gale = get_rent_gale(rentobj.lastrentdate, rentobj.freq_id, rentobj.rentpa)
        altered_arrears = rentobj.arrears - rent_gale
        update_rollback_rent(rent_id, altered_arrears)
        # save action to actions table
        action_str = 'pay request for rent ' + str(rent_id) + ' totalling ' + str(
            pr_file.total_due) + ' has been undone'
        add_action(2, 0, action_str, 'pr_bp.pr_history', {'rent_id': rent_id})
        commit_to_database()
        message = "Pay request undone!"
    except Exception as err:
        return type(err), rent_id
    return message, rent_id


def update_pr_delivered(pr_id):
    pr_file = get_pr_history_row(pr_id)
    if (not pr_file.delivered) and pr_file.delivery_method == 2:  # post delivery
        post_updated_payrequest_delivery(True, pr_file)


def write_payrequest(rent_id, pr_form_id):
    rent_pr = get_rentp(rent_id)  # get full enhanced rent pack
    rent_pr = append_pr_history_details(rent_pr)
    pr_variables = get_rent_strings(rent_pr, 'payrequest')
    arrears_clause, create_case, new_arrears, new_arrears_level, new_charge_dict, table_rows, \
    rent_pr.totdue = build_pr_table(rent_pr, pr_variables)
    pr_variables.update({'#totdue#': moneyToStr(rent_pr.totdue, pound=True) if rent_pr.totdue else "no total due"})
    subject = "{} account for property: #propaddr#".format(rent_pr.rent_type.capitalize())
    subject = doReplace(pr_variables, subject)
    pr_form = get_pr_form(pr_form_id)
    arrears_clause = doReplace(pr_variables, arrears_clause) + '\n\n' if arrears_clause else ""
    block = arrears_clause.capitalize() + doReplace(pr_variables, pr_form.block) if pr_form.block else ""
    # TODO: pr_save_data can be cleaned up if we are passing all pr_variables in the dictionary
    pr_save_data = {
        'new_arrears': new_arrears,
        'create_case': create_case,
        'new_arrears_level': new_arrears_level,
        'new_charge_dict': new_charge_dict,
        'pr_code': pr_form.code,
        'rent_date_string': dateToStr(rent_pr.nextrentdate),
        'tot_due': rent_pr.totdue,
        'pr_variables': pr_variables
    }
    return block, pr_save_data, rent_pr, subject, table_rows


def write_payrequest_x(rent_id, pr_form_id):
    rent_pr = get_rentp(rent_id)  # get full enhanced rent pack
    rent_pr = append_pr_history_details(rent_pr)
    pr_form = get_pr_form(pr_form_id)
    rent_pr.pr_code = pr_form.code
    rent_pr.suffix = build_charges_suffix(rent_pr)
    rent_pr.create_case, recovery_charge_amount = get_recovery_info_x(rent_pr.suffix)
    rent_pr.new_arrears_level = build_new_arrears_level_string(rent_pr.suffix)
    includes_recovery = check_recovery_in_charges(rent_pr.charges, recovery_charge_amount)
    rent_pr.recovery_charge_amount = 0
    if recovery_charge_amount > 0 and not includes_recovery:
        rent_pr.recovery_charge_amount = recovery_charge_amount
        rent_pr.totcharges = rent_pr.totcharges + recovery_charge_amount
    rent_pr = append_pr_date_variables(rent_pr)
    return rent_pr


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
