import sqlalchemy
from sqlalchemy import func, select
from app.models import Charge, Chargetype, PRArrearsMatrix, PRHistory, Rent
from app import db
from flask_table import Table, Col
from app.main.functions import dateToStr
from locale import currency
import datetime


def forward_rents(rentprops):
    for rent_prop in rentprops:
        forward_rent(rent_prop.id)


def forward_rent(rent_id):
    rent = Rent.query.get(rent_id)
    update_last_rent_date(rent)
    update_arrears(rent)
    db.session.commit()


def update_arrears(rent):
    previous_arrears = rent.arrears
    rent_gale = rent.rentpa / rent.freq_id
    rent.arrears = previous_arrears + rent_gale


# Arguments for next_rent_date: (rentid int, rentype int, periods int) RETURNS list of dates
def update_last_rent_date(rent):
    rent.lastrentdate = db.session.execute(func.mjinn.next_rent_date(rent.id, 1, 1)).scalar()


def get_pay_request_table_charges(rent_id):
    charges = get_charge_details(rent_id)
    charge_table_items = {}
    for charge in charges:
        charge_detail = "{} added on {}:".format(charge.chargedesc.capitalize(), dateToStr(charge.chargestartdate))
        charge_total = charge.chargetotal
        charge_table_items.update({charge_detail: charge_total})
    return charge_table_items


def get_charge_details(rent_id):
    qfilter = [Charge.rent_id == rent_id]
    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                     Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(*qfilter).all()
    return charges


def determine_new_charges_and_case_suffix(rentobj):
    periods = rentobj.arrears * rentobj.freq_id / rentobj.rentpa
    charges_total = rentobj.totcharges
    pr_exists = check_previous_pr_exists(rentobj.id)
    last_recovery_level = get_last_recovery_level(rentobj.id) if pr_exists else ""
    # TODO: This is labeled "oldestchargedate" in Jinn. Should it be "most_recent_charge_start_date"?
    oldest_charge_date = db.session.execute(func.mjinn.oldest_charge(rentobj.id)).scalar()
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


def check_previous_pr_exists(rent_id):
    exists = bool(db.session.query(PRHistory).filter_by(rent_id=rent_id).first())
    return exists


def get_last_recovery_level(rent_id):
    last_recovery_level = db.session.execute(func.mjinn.last_recovery_level(rent_id)).scalar()
    return last_recovery_level


def get_rent_statement(rentobj, rent_type):
    if rentobj.freq_id == 1:
        freq = "One year's"
    elif rentobj.freq_id == 2:
        freq = "One half-year's"
    elif rentobj.freq_id == 4:
        freq = "One quarter's"
    elif rentobj.freq_id == 12:
        freq = "One month's"
    elif rentobj.freq_id == 13:
        freq = "One four weekly"
    else:
        freq = "One weekly"

    if rentobj.nextrentdate > datetime.date.today():
        f = "falls"
    else:
        f = "fell"

    statement = "{0} {1} {2} due and payable {3} on {4}:".format(freq, rent_type, f,
                                                                 rentobj.advarrdet, dateToStr(rentobj.nextrentdate))
    return statement


def get_arrears_statement(rent_type, arrears_start_date, arrears_end_date):
    statement = "Unpaid {0} is owing for the period {1} to {2}:".format(rent_type, arrears_start_date, arrears_end_date)
    return statement


# Code to build PR tables
# Format the currency column
class CurrencyCol(Col):
    def td_format(self, content):
        content = float(content)
        # locale.setlocale(locale.LC_NUMERIC, '')
        return "£{:,.2f}".format(content)


class PayRequestItem(object):
    def __init__(self, details, amount):
        self.details = details
        self.amount = amount

    # identify the 'total amount' row
    def important(self):
        return self.details.lower().find("total amount") != -1


class PayRequestTable(Table):
    classes = ['pr_table']
    details = Col('Details')
    amount = CurrencyCol(
        'Amount',
        td_html_attrs={
            'class': 'amount-class'},
    )

    # assign a class to the 'total' row so we can style it with css
    def get_tr_attrs(self, payrequest_item):
        if payrequest_item.important():
            return {'class': 'total'}
        else:
            return {}


def build_pr_table(list_amounts):
    items = []
    for key in list_amounts:
        items.append(PayRequestItem(key, list_amounts[key]))
    return items


class RecoveryLevel:
    Normal = ""
    Warning = "W"
    First = "1"
    Second = "2"
    Third = "3"
    Fourth = "4"
