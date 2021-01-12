import json
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, literal
from app.models import Case, Charge, Chargetype, Pr_arrears_matrix, Pr_history, Rent
from app import db
from app.main.functions import dateToStr, commit_to_database, moneyToStr
from datetime import date, datetime, timedelta
from decimal import Decimal
from flask import request


def forward_rents(rentobjs):
    update_vals = []
    for rent_prop in rentobjs:
        update_vals.append(forward_rent(rent_prop.id, True))
    db.session.bulk_update_mappings(Rent, update_vals)
    commit_to_database()


def forward_rent(rent_id, from_batch=False):
    rent = Rent.query.get(rent_id)
    last_rent_date = db.session.execute(func.samjinn.next_rent_date(rent_id, 1, 1)).scalar()
    arrears = rent.arrears + (rent.rentpa / rent.freq_id)
    if not from_batch:
        rent.lastrentdate = last_rent_date
        rent.arrears = arrears
        commit_to_database()
    else:
        return dict(id=rent_id, lastrentdate=last_rent_date, arrears=arrears)


# TODO: Decide if database queries should have their own module (probably)
def get_rent_charge_details(rent_id):
    qfilter = [Charge.rent_id == rent_id]
    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                                                                     Charge.chargestartdate, Charge.chargetotal,
                                                                     Charge.chargedetails, Charge.chargebalance) \
        .filter(*qfilter).all()
    return charges


def check_recovery_in_charges(charges, recovery_charge_amount):
    includes_recovery = False
    for charge in charges:
        if charge.chargetotal == recovery_charge_amount and charge.chargedesc == "recovery costs":
            includes_recovery = True
    return includes_recovery


def create_pr_charges_table(rentobj):
    charges = get_rent_charge_details(rentobj.id)
    charge_table_items = {}
    new_charge_dict = {}
    total_charges = 0
    for charge in charges:
        charge_details = "{} added on {}:".format(charge.chargedesc.capitalize(), dateToStr(charge.chargestartdate))
        charge_total = charge.chargetotal
        charge_table_items.update({charge_details: moneyToStr(charge_total, pound=True)})
        total_charges = total_charges + charge_total
    # TODO: Store new_charge object to save later, add create_case logic
    suffix = determine_charges_suffix(rentobj)
    arrears_clause, create_case, recovery_charge_amount = get_recovery_info(suffix)
    new_arrears_level = get_new_arrears_level(suffix)
    if recovery_charge_amount > 0 and not check_recovery_in_charges(charges, recovery_charge_amount):
        new_charge_dict = create_charge_dict(rentobj.id, recovery_charge_amount, 10)
        charge_details = "{} added on {}:".format("Recovery costs", dateToStr(datetime.date.today()))
        charge_table_items.update({charge_details: moneyToStr(recovery_charge_amount, pound=True)})
        total_charges = total_charges + recovery_charge_amount

    return arrears_clause, charge_table_items, create_case, total_charges, new_charge_dict, new_arrears_level


def check_charge_exists(rent_id, charge_total, charge_type_id):
    return db.session.query(literal(True)).filter(Charge.rent_id == rent_id,
                                                  Charge.chargetype_id == charge_type_id,
                                                  Charge.chargetotal == charge_total)


# TODO: Can we combine all pr variables into a single json dict, or as a pr class object?
def create_charge_dict(rent_id, charge_total, charge_type_id):
    new_charge_dict = {
        'rent_id': rent_id,
        'charge_total': charge_total,
        'charge_type_id': charge_type_id
    }
    return new_charge_dict


def create_case(rent_id):
    case = Case()
    case.id = rent_id
    case.case_details = "Automatically created on {}".format(dateToStr(date.today()))
    case.case_nad = date.today() + relativedelta(days=30)
    db.session.merge(case)


def get_recovery_info(suffix):
    recovery_info = Pr_arrears_matrix.query.with_entities(Pr_arrears_matrix.arrears_clause,
                                                                      Pr_arrears_matrix.recovery_charge,
                                                                      Pr_arrears_matrix.create_case).\
        filter_by(suffix=suffix).one_or_none()
    arrears_clause = recovery_info.arrears_clause
    create_case = recovery_info.create_case
    recovery_charge = recovery_info.recovery_charge
    return arrears_clause, create_case, recovery_charge


def determine_charges_suffix(rentobj):
    periods = rentobj.arrears * rentobj.freq_id / rentobj.rentpa
    charges_total = rentobj.totcharges if rentobj.totcharges else 0
    pr_exists = check_previous_pr_exists(rentobj.id)
    last_arrears_level = get_last_arrears_level(rentobj.id) if pr_exists else ""
    # TODO: This is labeled "oldestchargedate" in Jinn. Should it be "most_recent_charge_start_date"?
    oldest_charge_date = db.session.execute(func.samjinn.oldest_charge(rentobj.id)).scalar()
    charge_90_days = oldest_charge_date and date.today() - oldest_charge_date > timedelta(90)
    return get_charges_suffix(periods, charges_total, pr_exists, last_arrears_level, charge_90_days)


def get_charges_suffix(periods, charges_total, pr_exists, last_arrears_level, charge_90_days):
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


def get_new_arrears_level(suffix):
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


def add_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(date.today())
    charge_type = get_charge_type(chargetype_id)
    charge_details = "£{} {} added on {}".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    new_charge = Charge(id=0, chargetype_id=chargetype_id, chargestartdate=date.today(),
                        chargetotal=recovery_charge_amount, chargedetails=charge_details,
                        chargebalance=recovery_charge_amount, rent_id=rent_id)
    db.session.add(new_charge)


def get_charge_type(chargetype_id):
    return db.session.query(Chargetype.chargedesc).filter_by(id=chargetype_id).scalar()


def check_previous_pr_exists(rent_id):
    exists = bool(db.session.query(Pr_history).filter_by(rent_id=rent_id).first())
    return exists


# TODO: check that arrears_level is best recorded in pr_history and where to signal if pr delivery is complete -
# TODO: currently if delivery_method > 3 in pr_history, then delivery is incomplete. This value is used in last_arrears_level
def get_last_arrears_level(rent_id):
    last_arrears_level = db.session.execute(func.samjinn.last_arrears_level(rent_id)).scalar()
    return last_arrears_level


def get_rent_statement(rentobj, rent_type):
    statement = "The {0} {1} due and payable {2} on {3}:".format(rentobj.freqdet, rent_type, rentobj.advarrdet, dateToStr(rentobj.nextrentdate))
    return statement


def get_arrears_statement(rent_type, arrears_start_date, arrears_end_date):
    statement = "Unpaid {0} is owing for the period {1} to {2}:".format(rent_type, arrears_start_date, arrears_end_date)
    return statement


def get_pr_file(id):
    pr_file = Pr_history.query.join(Rent).with_entities(Pr_history.id, Pr_history.summary, Pr_history.block,
                                                        Pr_history.date, Rent.rentcode,
                                                        Rent.id.label("rent_id")) \
                                                        .filter(Pr_history.id == id).one_or_none()

    return pr_file


def get_pr_history(rent_id):
    return Pr_history.query.filter_by(rent_id=rent_id)


# TODO: Improve editing functionality. Do we want the (email) subject saved anywhere? - currently in a hidden input in PR.html
def post_pr_file(id=0):
    pr_data = json.loads(request.form.get('pr_data'))
    rent_id = pr_data.get("rent_id")
    # New payrequest
    if id == 0:
        pr_history = Pr_history()
        pr_history.id = 0
        pr_history.rent_id = rent_id
        pr_history.date = request.form.get('date')
        # TODO: Update batch_id logic when we have multiple payrequest
        # pr_history.batch_id = 0
        pr_history.rent_date = datetime.strptime(pr_data.get("rent_date_string"), '%Y-%m-%d')
        pr_history.total_due = pr_data.get("tot_due")
        pr_history.arrears_level = pr_data.get("new_arrears_level")
        # TODO: Hardcoded check of delivery method, must be changed if new delivery methods are added (emailed and mailed)
        pr_history.delivery_method = 1 if request.form.get('method') == "email" else 2
    # Old payrequest
    else:
        pr_history = Pr_history.query.get(id)

    pr_history.summary = request.form.get('summary')
    pr_history.block = request.form.get('xinput').replace("£", "&pound;")

    db.session.add(pr_history)

    if id == 0:
        forward_rent(rent_id)
        new_charge_dict = pr_data.get("new_charge_dict")
        if len(new_charge_dict) > 0:
            add_charge(new_charge_dict.get("rent_id"), Decimal(new_charge_dict.get("charge_total")),
                       new_charge_dict.get("charge_type_id"))
        if pr_data.get("create_case"):
            create_case(rent_id)

    commit_to_database()

    return rent_id


class ArrearsLevel:
    Normal = ""
    Warning = "W"
    First = "1"
    Second = "2"
    Third = "3"
    Fourth = "4"
