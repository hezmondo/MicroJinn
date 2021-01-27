import json

from app import db, decimal_default
from app.dao.functions import dateToStr, commit_to_database
from app.models import Case, Charge, Chargetype, Landlord, Manager, Money_account, Pr_arrears_matrix, \
                        Pr_form, Pr_history, Rent, Typeadvarr, Typefreq, Typetenure
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from flask import request
from sqlalchemy import func


def add_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(date.today())
    charge_type = get_charge_type(chargetype_id)
    charge_details = "£{} {} added on {}".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    new_charge = Charge(id=0, chargetype_id=chargetype_id, chargestartdate=date.today(),
                        chargetotal=recovery_charge_amount, chargedetail=charge_details,
                        chargebalance=recovery_charge_amount, rent_id=rent_id)
    db.session.add(new_charge)


def add_forward_rent(rent_id, from_batch=False):
    rent = Rent.query.get(rent_id)
    last_rent_date = db.session.execute(func.mjinn.next_rent_date(rent_id, 1, 1)).scalar()
    arrears = calculate_arrears(rent.arrears, rent.freq_id, rent.rentpa)
    if not from_batch:
        rent.lastrentdate = last_rent_date
        rent.arrears = arrears
        # TODO: Does add() need to be called if we do not commit here
        # db.session.add(rent)
        # commit_to_database()
    else:
        return dict(id=rent_id, lastrentdate=last_rent_date, arrears=arrears)


def add_forward_rents(rent_prs):
    update_vals = []
    for rent_prop in rent_prs:
        update_vals.append(add_forward_rent(rent_prop.id, True))
    # TODO: Does add() need to be called if we do not commit here
    db.session.bulk_update_mappings(Rent, update_vals)
    # commit_to_database()


def calculate_arrears(arrears, freq_id, rent_pa):
    return arrears + (rent_pa / freq_id)


def get_charge_start_date(rent_id):
    return db.session.execute(func.mjinn.oldest_charge(rent_id)).scalar()


def get_charge_type(chargetype_id):
    return db.session.query(Chargetype.chargedesc).filter_by(id=chargetype_id).scalar()


def get_pr_data(pr_data):
    pr_data = json.dumps(pr_data, default=decimal_default)
    return pr_data


def get_pr_form(pr_form_id):
    pr_form = Pr_form.query.filter(Pr_form.id == pr_form_id).one_or_none()
    return pr_form


def get_pr_forms():
    return Pr_form.query.all()


def get_pr_file(pr_id):
    pr_file = Pr_history.query.join(Rent).with_entities(Pr_history.id, Pr_history.summary, Pr_history.block,
                                                        Pr_history.date, Rent.rentcode,
                                                        Rent.id.label("rent_id")) \
        .filter(Pr_history.id == pr_id).one_or_none()
    return pr_file


def get_pr_history(rent_id):
    return Pr_history.query.filter_by(rent_id=rent_id)


def get_previous_pr_history_entry(pr_id):
    pr_history = Pr_history.query.get(pr_id)
    rent_id = pr_history.rent_id
    return pr_history, rent_id


def get_recovery_info(suffix):
    recovery_info = Pr_arrears_matrix.query.with_entities(Pr_arrears_matrix.arrears_clause,
                                                          Pr_arrears_matrix.recovery_charge,
                                                          Pr_arrears_matrix.create_case). \
        filter_by(suffix=suffix).one_or_none()
    arrears_clause = recovery_info.arrears_clause
    create_case = recovery_info.create_case
    recovery_charge = recovery_info.recovery_charge
    return arrears_clause, create_case, recovery_charge


def get_rent_charge_details(rent_id):
    qfilter = [Charge.rent_id == rent_id]
    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                                                                     Charge.chargestartdate, Charge.chargetotal,
                                                                     Charge.chargedetail, Charge.chargebalance) \
        .filter(*qfilter).all()
    return charges


def get_rent_pr(rent_id):
    rent_pr = \
        Rent.query \
            .join(Landlord) \
            .join(Manager) \
            .join(Money_account) \
            .join(Typeadvarr) \
            .join(Typefreq) \
            .join(Typetenure) \
            .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.check_pr_exists(Rent.id).label('prexists'),
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.next_rent_date(Rent.id, 1, 2).label('nextrentdate_plus1'),
                           func.mjinn.next_rent_date(Rent.id, 1, 3).label('nextrentdate_plus2'),
                           func.mjinn.paid_to_date(Rent.id).label('paidtodate'),
                           func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           # TODO: check that arrears_level is best recorded in pr_history and where to signal if pr delivery is complete -
                           # TODO: currently if delivery_method > 3 in pr_history, then delivery is incomplete. This value is used in last_arrears_level
                           func.mjinn.last_arrears_level(Rent.id).label('lastarrearslevel'),
                           Rent.rentpa, Rent.tenantname, Rent.freq_id,
                           Manager.managername, Manager.manageraddr, Manager.manageraddr2,
                           Money_account.bank_name, Money_account.acc_name, Money_account.acc_num, Money_account.sort_code,
                           Typeadvarr.advarrdet, Typefreq.freqdet, Typetenure.tenuredet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()
    return rent_pr


def merge_case(rent_id, pr_id):
    case = Case()
    case.id = rent_id
    case.case_details = "Automatically created by payrequest {} on {}".format(pr_id, dateToStr(date.today()))
    case.case_nad = date.today() + relativedelta(days=30)
    db.session.merge(case)


# # TODO: Improve editing functionality. Do we want the (email) subject saved anywhere? - currently in a hidden input in PR.html
# def post_pr_history(pr_id=0):
#     # New payrequest
#     if pr_id == 0:
#         pr_data = json.loads(request.form.get('pr_data'))
#         rent_id = pr_data.get("rent_id")
#         pr_history = Pr_history()
#         pr_history.rent_id = rent_id
#         pr_history.date = request.form.get('date')
#         pr_history.rent_date = datetime.strptime(pr_data.get("rent_date_string"), '%Y-%m-%d')
#         pr_history.total_due = pr_data.get("tot_due")
#         pr_history.arrears_level = pr_data.get("new_arrears_level")
#         # TODO: Hardcoded check of delivery method, must be changed if new delivery methods are added (emailed and mailed)
#         pr_history.delivery_method = 1 if request.form.get('method') == "email" else 2
#     # Old payrequest
#     else:
#         pr_history = Pr_history.query.get(pr_id)
#         rent_id = pr_history.rent_id
#     pr_history.summary = request.form.get('summary')
#     pr_history.block = request.form.get('xinput').replace("£", "&pound;")
#     db.session.add(pr_history)
#     db.session.flush()
#     if pr_id == 0:
#         post_forward_rent(rent_id)
#         new_charge_dict = pr_data.get("new_charge_dict")
#         if len(new_charge_dict) > 0:
#             add_charge(new_charge_dict.get("rent_id"), Decimal(new_charge_dict.get("charge_total")),
#                        new_charge_dict.get("charge_type_id"))
#         if pr_data.get("create_case"):
#             merge_case(rent_id, pr_history.id)
#     commit_to_database()
#     return rent_id


def post_payrequest(pr_id=0):
    # TODO: Improve editing functionality. Do we want the (email) subject saved anywhere? \
    #  - currently in a hidden input in PR.html
    if pr_id == 0:
        pr_data, pr_history, rent_id = prepare_new_pr_history_entry()
    else:
        pr_history, rent_id = get_previous_pr_history_entry(pr_id)
    prepare_summary_block_entry(pr_history)
    db.session.add(pr_history)
    db.session.flush()
    if pr_id == 0:
        add_forward_rent_case_and_charges(pr_history, pr_data, rent_id)
    # TODO test if forward_rents changes are committed to the db without add being called on
    commit_to_database()
    return rent_id


def prepare_new_pr_history_entry():
    pr_data = json.loads(request.form.get('pr_data'))
    rent_id = pr_data.get("rent_id")
    pr_history = Pr_history()
    pr_history.rent_id = rent_id
    pr_history.date = request.form.get('date')
    pr_history.rent_date = datetime.strptime(pr_data.get("rent_date_string"), '%Y-%m-%d')
    pr_history.total_due = pr_data.get("tot_due")
    pr_history.arrears_level = pr_data.get("new_arrears_level")
    # TODO: Hardcoded check of delivery method, must be changed if new delivery methods are added (emailed and mailed)
    pr_history.delivery_method = 1 if request.form.get('method') == "email" else 2
    return pr_data, pr_history, rent_id


def prepare_summary_block_entry(pr_history):
    pr_history.summary = request.form.get('summary')
    pr_history.block = request.form.get('xinput').replace("£", "&pound;")


def add_forward_rent_case_and_charges(pr_history, pr_data, rent_id):
    add_forward_rent(rent_id)
    new_charge_dict = pr_data.get("new_charge_dict")
    if len(new_charge_dict) > 0:
        add_charge(new_charge_dict.get("rent_id"), Decimal(new_charge_dict.get("charge_total")),
                   new_charge_dict.get("charge_type_id"))
    if pr_data.get("create_case"):
        merge_case(rent_id, pr_history.id)
