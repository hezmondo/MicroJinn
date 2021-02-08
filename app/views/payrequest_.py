from werkzeug.datastructures import MultiDict
from app.dao.filter import get_filters
from app.dao.functions import doReplace, moneyToStr, dateToStr
from app.dao.payrequest_ import get_charge_start_date, serialize_pr_save_data, get_pr_form, get_pr_forms, get_pr_file, \
    get_pr_history, get_recovery_info, get_rent_charge_details, get_rent_pr, post_new_payrequest, \
    post_updated_payrequest
from app.dao.rent_ import get_rent_mail
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from app.forms import PrPostForm


pr_bp = Blueprint('pr_bp', __name__)


@pr_bp.route('/pr_dialog/<int:rent_id>', methods=["GET", "POST"])
@login_required
def pr_dialog(rent_id):
    pr_forms = get_pr_forms()
    rent_mail = get_rent_mail(rent_id)
    return render_template('pr_dialog.html', pr_forms=pr_forms, rent_id=rent_id, rent_mail=rent_mail)


@pr_bp.route('/pr_edit/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit(pr_form_id):
    if request.method == "POST":
        # method = request.args.get('method', 'post', type=str)
        rent_id = request.args.get('rent_id')
        # TODO: Avoid passing both totdue and totdue_string - include money formatting in html template?
        block, pr_save_data, rent_pr, subject, table_rows, \
            totdue_string = write_payrequest(rent_id, pr_form_id)
        # if method == 'email':
        #     pr_form = PrEmailForm(formdata=MultiDict({'email': rent_pr.email, 'subject': subject}))
        # elif method == 'post':
        pr_form = PrPostForm()
        rent_mail = get_rent_mail(rent_id)
        mailaddr = rent_mail.mailaddr.split(", ")
        pr_form.mailaddr.choices = [rent_mail.mailaddr, (rent_mail.tenantname + ', ' + rent_mail.propaddr),
                                    ('The owner/occupier, ' + rent_mail.propaddr)]
        if pr_form.validate_on_submit():
            return redirect(url_for('pr_save_send', rent_id=rent_pr.id))
        pr_save_data = serialize_pr_save_data(pr_save_data)
        return render_template('mergedocs/PR.html', mailaddr=mailaddr, pr_save_data=pr_save_data, pr_form=pr_form,
                               block=block, rent_pr=rent_pr, subject=subject,
                               table_rows=table_rows, totdue_string=totdue_string)


@pr_bp.route('/pr_email_edit', methods=["GET", "POST"])
@login_required
def pr_email_edit(pr_form_id):
    if request.method == "POST":
        return render_template('mergedocs/PR.html')


# TODO: improve pr_file editing functionality (beyond edit summary/block)
@pr_bp.route('/pr_file/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_file(pr_id):
    if request.method == "POST":
        rent_id = post_updated_payrequest(pr_id)
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id))
    pr_file = get_pr_file(pr_id)
    return render_template('pr_file.html', pr_file=pr_file)


@pr_bp.route('/pr_history/<int:rent_id>', methods=['GET', 'POST'])
def pr_history(rent_id):
    pr_history = get_pr_history(rent_id)
    return render_template('pr_history.html', rent_id=rent_id, pr_history=pr_history)


# @bp.route('/pr_main/<int:id>', methods=['GET', 'POST'])
# @login_required
# def pr_main(id):
#     actypedets, floads, options, prdeliveries, salegradedets = get_queryoptions_advanced()
#     landlords, statusdets, tenuredets = get_queryoptions_common()
#     if id == 0:
#         rentprops = get_rentobjs_filter(1)
#     else:
#         rentprops = get_rentobjs_filter(id)
#
#     return render_template('pr_main.html', actypedets=actypedets, floads=floads, options=options,
#                            prdeliveries=prdeliveries, salegradedets=salegradedets, landlords=landlords,
#                            statusdets=statusdets, tenuredets=tenuredets, rentprops=rentprops)


@pr_bp.route('/pr_save_send', methods=['GET', 'POST'])
def pr_save_send():
    method = request.args.get('method', type=str)
    if request.method == "POST":
        id_ = post_new_payrequest(method)
        return redirect(url_for('pr_bp.pr_history', rent_id=id_))


@pr_bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    filters = get_filters(1)
    return render_template('pr_start.html', filters=filters)


def build_arrears_statement(rent_type, arrears_start_date, arrears_end_date):
    statement = "Unpaid {0} is owing for the period {1} to {2}:".format(rent_type, arrears_start_date, arrears_end_date)
    return statement


def build_charges_suffix(rent_pr):
    periods = calculate_periods(rent_pr.arrears, rent_pr.freq_id, rent_pr.rentpa)
    charges_total = rent_pr.totcharges if rent_pr.totcharges else 0
    pr_exists = True if rent_pr.prexists == 1 else False
    last_arrears_level = rent_pr.lastarrearslevel if pr_exists else ""
    charge_start_date = get_charge_start_date(rent_pr.id)
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


def build_pr_variables(rent_pr):
    arrears = rent_pr.arrears if rent_pr.arrears else Decimal(0)
    arrears_start_date = dateToStr(rent_pr.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rent_pr.nextrentdate + relativedelta(days=-1)) \
        # if rent_pr.advarrdet == "in advance" else dateToStr(rent_pr.lastrentdate)
    # TODO: Check if rentobj.tenuredet == "Rentcharge" below
    rent_type = "rent charge" if rent_pr.tenuredet == "Rentcharge" else "ground rent"
    totcharges = rent_pr.totcharges if rent_pr.totcharges else Decimal(0)
    totdue = arrears + totcharges
    pr_variables = {'#acc_name#': rent_pr.acc_name if rent_pr.acc_name else "no acc_name",
                    '#acc_num#': rent_pr.acc_num if rent_pr.acc_num else "no acc_number",
                    '#sort_code#': rent_pr.sort_code if rent_pr.sort_code else "no sort_code",
                    '#bank_name#': rent_pr.bank_name if rent_pr.bank_name else "no bank_name",
                    '#arrears#': moneyToStr(arrears, pound=True),
                    '#lastrentdate#': dateToStr(rent_pr.lastrentdate) if rent_pr else "11/11/1111",
                    '#managername#': rent_pr.managername if rent_pr else "no manager name",
                    '#manageraddr#': rent_pr.manageraddr if rent_pr else "no manager address",
                    '#manageraddr2#': rent_pr.manageraddr2 if rent_pr else "no manager address2",
                    '#nextrentdate#': dateToStr(rent_pr.nextrentdate) if rent_pr else "no nextrentdate",
                    '#propaddr#': rent_pr.propaddr if rent_pr else "no property address",
                    '#rentcode#': rent_pr.rentcode if rent_pr else "no rentcode",
                    '#arrears_start_date#': arrears_start_date,
                    '#arrears_end_date#': arrears_end_date,
                    '#rentpa#': moneyToStr(rent_pr.rentpa, pound=True) if rent_pr else "no rent",
                    '#rent_type#': rent_type,
                    '#tenantname#': rent_pr.tenantname if rent_pr else "no tenant name",
                    '#totcharges#': moneyToStr(totcharges, pound=True),
                    '#totdue#': moneyToStr(totdue, pound=True) if totdue else "no total due",
                    '#today#': dateToStr(date.today())
                    }
    return pr_variables


def build_rent_statement(rent_pr, rent_type):
    statement = "{0} {1} due and payable {2} on {3}:".format(rent_pr.freqdet, rent_type, rent_pr.advarrdet,
                                                                 dateToStr(rent_pr.nextrentdate))
    return statement


def calculate_periods(arrears, freq_id, rent_pa):
    return arrears * freq_id / rent_pa


def check_recovery_in_charges(charges, recovery_charge_amount):
    includes_recovery = False
    for charge in charges:
        if charge.chargetotal == recovery_charge_amount and charge.chargedesc == "recovery costs":
            includes_recovery = True
    return includes_recovery


def build_pr_charges_table(rent_pr):
    charges = get_rent_charge_details(rent_pr.id)
    charge_table_items = {}
    new_charge_dict = {}
    total_charges = 0
    for charge in charges:
        charge_details = "{} added on {}:".format(charge.chargedesc.capitalize(), dateToStr(charge.chargestartdate))
        charge_total = charge.chargetotal
        charge_table_items.update({charge_details: moneyToStr(charge_total, pound=True)})
        total_charges = total_charges + charge_total
    suffix = build_charges_suffix(rent_pr)
    arrears_clause, create_case, recovery_charge_amount = get_recovery_info(suffix)
    new_arrears_level = build_new_arrears_level_string(suffix)
    if recovery_charge_amount > 0 and not check_recovery_in_charges(charges, recovery_charge_amount):
        charge_details = "{} added on {}:".format("Recovery costs", dateToStr(date.today()))
        charge_table_items.update({charge_details: moneyToStr(recovery_charge_amount, pound=True)})
        total_charges = total_charges + recovery_charge_amount
        new_charge_dict = {
            'rent_id': rent_pr.id,
            'charge_total': recovery_charge_amount,
            'charge_type_id': 10
        }
    return arrears_clause, charge_table_items, create_case, total_charges, new_charge_dict, new_arrears_level


def build_pr_table(rent_pr, pr_variables):
    rent_gale = (rent_pr.rentpa / rent_pr.freq_id) if rent_pr.rentpa != 0 else 0
    arrears = rent_pr.arrears
    arrears_start_date = pr_variables.get('#arrears_start_date#')
    arrears_end_date = pr_variables.get('#arrears_end_date#')
    rent_type = pr_variables.get('#rent_type#')
    table_rows = {}
    if rent_gale:
        rent_statement = build_rent_statement(rent_pr, rent_type)
        table_rows.update({rent_statement: moneyToStr(rent_gale, pound=True)})
    if arrears:
        arrears_statement = build_arrears_statement(rent_type, arrears_start_date, arrears_end_date)
        table_rows.update({arrears_statement: moneyToStr(arrears, pound=True)})
    arrears_clause, charge_table_items, create_case, total_charges, \
        new_charge_dict, new_arrears_level = build_pr_charges_table(rent_pr)
    if total_charges:
        table_rows.update(charge_table_items)
    totdue = rent_gale + arrears + total_charges
    return arrears_clause, create_case, new_arrears_level, new_charge_dict, rent_type, table_rows, totdue


def write_payrequest(rent_id, pr_form_id):
    rent_pr = get_rent_pr(rent_id)
    pr_variables = build_pr_variables(rent_pr)
    arrears_clause, create_case, new_arrears_level, new_charge_dict, rent_type, table_rows, totdue = \
        build_pr_table(rent_pr, pr_variables)
    totdue_string = moneyToStr(totdue, pound=True) if totdue else "no total due"
    pr_variables.update({'#totdue#': totdue_string})
    subject = "{} account for property: #propaddr#".format(rent_type.capitalize())
    subject = doReplace(pr_variables, subject)
    pr_form = get_pr_form(pr_form_id)
    arrears_clause = doReplace(pr_variables, arrears_clause) + '\n\n' if arrears_clause else ""
    block = arrears_clause.capitalize() + doReplace(pr_variables, pr_form.block) if pr_form.block else ""
    pr_save_data = {
        'create_case': create_case,
        'new_arrears_level': new_arrears_level,
        'new_charge_dict': new_charge_dict,
        'pr_code': pr_form.code,
        'rent_date_string': str(rent_pr.nextrentdate),
        'tot_due': totdue
    }
    return block, pr_save_data, rent_pr, subject, table_rows, totdue_string


class ArrearsLevel:
    Normal = ""
    Warning = "W"
    First = "1"
    Second = "2"
    Third = "3"
    Fourth = "4"