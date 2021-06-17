import datetime
import json
from app import decimal_default
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import request, render_template
from dateutil.relativedelta import relativedelta
from app.dao.action import add_action
from app.dao.case import check_case_exists, add_case
from app.dao.charge import add_charge, get_charge_type, get_total_charges
from app.dao.database import commit_to_database
from app.main.doc import convert_html_to_pdf
from app.dao.form_letter import get_pr_form_essential, get_pr_form_code, get_pr_email_form
from app.dao.payrequest import post_pr_batch, add_pr_history, get_last_arrears_level, get_pr_charge, get_pr_file, get_pr_history_row, \
    get_recovery_info, get_recovery_info_x, prepare_new_pr_history_entry, \
    post_updated_payrequest_delivery, add_pr_charge
from app.dao.common import delete_record_basic
from app.dao.rent import get_rentcode
from app.main.functions import dateToStr, doReplace, moneyToStr
from app.main.rent import get_rent_gale, get_rentp, get_pr_strings, update_roll_rent, update_rollback_rent
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
    # TODO: Check what we want to do when last_arrears_level = 2. Jinn reverts back to warning.
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


def forward_rent_case_and_charges(pr_id, pr_rent_data, rent_id):
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


def run_batch(pr_template_id, rent_id_list, runcode):
    pr_complete = {}
    pr_error = {}
    for rent_id in rent_id_list:
        try:
            block, block_email, rent_pr, subject = write_payrequest(rent_id, pr_template_id)
            html = render_template('mergedocs/PR_template.html', block=block, rent_pr=rent_pr, subject=subject)
            pr_id = save_new_payrequest_from_batch(html, rent_pr)
            pr_complete[rent_id] = pr_id
        except Exception as ex:
            pr_error[rent_id] = str(ex)
    pr_batch = post_pr_batch(runcode, len(pr_complete), 'pending', False)
    return pr_batch, pr_complete, pr_error


def save_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(date.today())
    charge_type = get_charge_type(chargetype_id)
    charge_details = "£{} {} added on {}".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    charge_id = add_charge(rent_id, recovery_charge_amount, chargetype_id, charge_details)
    return charge_id


def save_new_payrequest(method, pr_history_data, pr_rent_data, rent_id):
    pr_history = prepare_new_pr_history_entry(pr_history_data, rent_id, method)
    # make a pdf to post or send as an attachment
    convert_html_to_pdf(pr_history_data.get('block'), 'pr.pdf')
    pr_id = add_pr_history(pr_history)
    case_created, charge_id = forward_rent_case_and_charges(pr_id, pr_rent_data, rent_id)
    if charge_id or case_created:
        add_pr_charge(pr_id, charge_id, case_created)
    # save action to actions table
    # TODO: Check with Hez - is it worth an extra db query to get the rentcode to display to the user rather than
    #  rent_id - get_rentcode(rent_id)
    action_str = 'Pay request for rent ' + get_rentcode(rent_id) + ' totalling ' + \
                 moneyToStr(pr_history_data.get('tot_due'), pound=True) + ' saved'
    add_action(2, 0, action_str, 'pr_bp.pr_history', {'rent_id': rent_id})
    commit_to_database()
    return pr_id


def save_new_payrequest_from_batch(html, rent_pr):
    pr_history_data = {'block': html,
                       'mailaddr': rent_pr.mailaddr,
                       'pr_code': rent_pr.pr_code,
                       'rent_date': rent_pr.nextrentdate.strftime("%Y-%m-%d"),
                       'tot_due': rent_pr.rent_gale + rent_pr.arrears + rent_pr.totcharges,
                       'new_arrears_level': rent_pr.new_arrears_level,
                       'new_arrears': rent_pr.arrears + rent_pr.rent_gale,
                       'charge_total': rent_pr.recovery_charge_amount}
    pr_history = prepare_new_pr_history_entry(pr_history_data, rent_pr.id, 'post')
    pr_id = add_pr_history(pr_history)
    pr_rent_data = {'rent_date': rent_pr.nextrentdate.strftime("%Y-%m-%d"),
                    'new_arrears': rent_pr.arrears + rent_pr.rent_gale,
                    'charge_total': rent_pr.recovery_charge_amount}
    case_created, charge_id = forward_rent_case_and_charges(pr_id, pr_rent_data, rent_pr.id)
    if charge_id or case_created:
        add_pr_charge(pr_id, charge_id, case_created)
    action_str = 'Pay request for rent ' + get_rentcode(rent_pr.id) + ' totalling ' + \
                 moneyToStr(pr_history_data.get('tot_due'), pound=True) + ' saved'
    add_action(2, 0, action_str, 'pr_bp.pr_history', {'rent_id': rent_pr.id})
    commit_to_database()
    return pr_id


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
        action_str = 'pay request for rent ' + get_rentcode(rent_id) + ' totalling ' + \
                     moneyToStr(pr_file.total_due, pound=True) + ' has been undone'
        add_action(2, 0, action_str, 'pr_bp.pr_history', {'rent_id': rent_id})
        commit_to_database()
        message = "Pay request undone!"
    except Exception as ex:
        return type(ex), rent_id
    return message, rent_id


def update_pr_delivered(pr_id):
    pr_file = get_pr_history_row(pr_id)
    if (not pr_file.delivered) and pr_file.delivery_method == 2:  # post delivery
        post_updated_payrequest_delivery(True, pr_file)


def write_payrequest(rent_id, pr_form_id):
    rent_pr = get_rentp(rent_id)  # get full enhanced rent pack
    rent_pr = append_pr_history_details(rent_pr)
    pr_form = get_pr_form_essential(pr_form_id)
    rent_pr.pr_code = pr_form.code
    rent_pr.suffix = build_charges_suffix(rent_pr)
    arrears_clause, rent_pr.create_case, recovery_charge_amount = get_recovery_info(rent_pr.suffix)
    rent_pr.new_arrears_level = build_new_arrears_level_string(rent_pr.suffix)
    includes_recovery = check_recovery_in_charges(rent_pr.charges, recovery_charge_amount)
    rent_pr.recovery_charge_amount = 0
    if recovery_charge_amount > 0 and not includes_recovery:
        rent_pr.recovery_charge_amount = recovery_charge_amount
        rent_pr.totcharges = rent_pr.totcharges + recovery_charge_amount
    rent_pr = append_pr_date_variables(rent_pr)
    pr_variables = get_pr_strings(rent_pr)
    subject = doReplace(pr_variables, pr_form.subject).title()
    arrears_clause = doReplace(pr_variables, arrears_clause) + '\n\n' if arrears_clause else ""
    block = arrears_clause.capitalize() + doReplace(pr_variables, pr_form.block) if pr_form.block else ""
    block_email = get_pr_email_form()
    block_email = doReplace(pr_variables, block_email.block)
    return block, block_email, rent_pr, subject


def write_payrequest_x(rent_id, pr_form_id):
    rent_pr = get_rentp(rent_id)  # get full enhanced rent pack
    rent_pr = append_pr_history_details(rent_pr)
    pr_form = get_pr_form_code(pr_form_id)
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


class ArrearsLevel:
    Normal = ""
    Warning = "W"
    First = "1"
    Second = "2"
