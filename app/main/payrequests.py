import sqlalchemy
from sqlalchemy import func, literal
from app.models import Charge, Chargetype, Pr_arrears_matrix, Rent
from app import db

from app.main.functions import dateToStr, commit_to_database, moneyToStr
from locale import currency
import datetime


def forward_rents(rentprops):
    update_vals = []
    for rent_prop in rentprops:
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


def check_or_add_recovery_charge(rentobj):
    charge_suffix = determine_charges_suffix(rentobj)
    recovery_charge_amount, create_case_info = get_recovery_info(charge_suffix)
    if recovery_charge_amount != 0:
        if not check_charge_exists(rentobj.id, 10, recovery_charge_amount):
            add_charge(rentobj.id, recovery_charge_amount, 10)


def check_charge_exists(rent_id, charge_type_id, charge_total):
    return db.session.query(literal(True)).filter(Charge.rent_id == rent_id,
                                                  Charge.chargetype_id == charge_type_id,
                                                  Charge.chargetotal == charge_total)


def get_recovery_info(suffix):
    recovery_charge = db.session.query(Pr_arrears_matrix.recovery_charge).filter_by(suffix=suffix).scalar()
    create_case_info = db.session.query(Pr_arrears_matrix.create_case).filter_by(suffix=suffix).scalar()
    return recovery_charge, create_case_info


def get_payrequest_table_charges(rent_id):
    charges = get_charge_details(rent_id)
    charge_table_items = {}
    total_charges = 0
    for charge in charges:
        charge_details = "{} added on {}:".format(charge.chargedesc.capitalize(), dateToStr(charge.chargestartdate))
        charge_total = charge.chargetotal
        charge_table_items.update({charge_details: moneyToStr(charge_total, pound=True)})
        total_charges = total_charges + charge_total
    return charge_table_items, total_charges


# TODO: Decide if database queries should have their own module (probably)
def get_charge_details(rent_id):
    qfilter = [Charge.rent_id == rent_id]
    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                                                                     Charge.chargestartdate, Charge.chargetotal,
                                                                     Charge.chargedetails, Charge.chargebalance) \
        .filter(*qfilter).all()
    return charges


def determine_charges_suffix(rentobj):
    periods = rentobj.arrears * rentobj.freq_id / rentobj.rentpa
    charges_total = rentobj.totcharges if rentobj.totcharges else 0
    pr_exists = check_previous_pr_exists(rentobj.id)
    last_recovery_level = get_last_recovery_level(rentobj.id) if pr_exists else ""
    # TODO: This is labeled "oldestchargedate" in Jinn. Should it be "most_recent_charge_start_date"?
    oldest_charge_date = db.session.execute(func.samjinn.oldest_charge(rentobj.id)).scalar()
    charge_90_days = oldest_charge_date and datetime.date.today() - oldest_charge_date > datetime.timedelta(90)
    return get_charges_suffix(periods, charges_total, pr_exists, last_recovery_level, charge_90_days)


def get_charges_suffix(periods, charges_total, pr_exists, last_recovery_level, charge_90_days):
    if periods == 0 and charges_total > 0 and charge_90_days:
        return "ZERACH"
    elif periods == 0:
        return "ZERA"
    elif periods > 0 and last_recovery_level == RecoveryLevel.Normal and not pr_exists:
        return "ZERA"
    elif periods > 0 and last_recovery_level == RecoveryLevel.Normal and pr_exists:
        return "ARW"
    elif periods > 1 and last_recovery_level == RecoveryLevel.Warning:
        return "ARC1"
    elif periods > 1 and last_recovery_level == RecoveryLevel.First:
        return "ARC2"
    elif periods > 2 and last_recovery_level == RecoveryLevel.Second:
        return "ARC3"
    elif periods > 3 and last_recovery_level == RecoveryLevel.Third:
        return "ARC4"
    else:
        return "ARW"


def add_charge(rent_id, recovery_charge_amount, chargetype_id):
    today_string = dateToStr(datetime.date.today())
    charge_type = Chargetype.chargedesc.filter_by(id=chargetype_id)
    charge_details = "£{} {} added on {}:".format(recovery_charge_amount, charge_type.capitalize(), today_string)
    new_charge = Charge(id=0, chargetype_id=chargetype_id, chargestartdate=today_string,
                        chargetotal=recovery_charge_amount, chargedetails=charge_details,
                        chargebalance=recovery_charge_amount, rent_id=rent_id)
    db.session.add(new_charge)
    commit_to_database()


# TODO: complete this using Payrequests model
def check_previous_pr_exists(rent_id):
    # exists = bool(db.session.query(PRHistory).filter_by(rent_id=rent_id).first())
    return False


def get_last_recovery_level(rent_id):
    last_recovery_level = db.session.execute(func.samjinn.last_recovery_level(rent_id)).scalar()
    return last_recovery_level


def get_rent_statement(rentobj, rent_type):
    statement = "The {0} {1} due and payable {2} on {3}:".format(rentobj.freqdet, rent_type, rentobj.advarrdet, dateToStr(rentobj.nextrentdate))
    return statement


def get_arrears_statement(rent_type, arrears_start_date, arrears_end_date):
    statement = "Unpaid {0} is owing for the period {1} to {2}:".format(rent_type, arrears_start_date, arrears_end_date)
    return statement


class RecoveryLevel:
    Normal = ""
    Warning = "W"
    First = "1"
    Second = "2"
    Third = "3"
    Fourth = "4"