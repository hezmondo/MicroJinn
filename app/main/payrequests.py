import sqlalchemy
from sqlalchemy import func, select
from app.models import Rent
from app import db
from flask_table import Table, Col
from locale import currency
from datetime import date


def forward_rents(rentprops, preview):
    for rent_prop in rentprops:
        rent = Rent.query.get(rent_prop.id)
        update_last_rent_date(rent)
        update_arrears(rent)
        if not preview:
            db.session.commit()
    return


# TODO: Refactor this - duplication of forward_rents
def forward_rent(rent_id, preview):
    rent = Rent.query.get(rent_id)
    update_last_rent_date(rent)
    update_arrears(rent)
    if not preview:
        db.session.commit()
    return


def update_arrears(rent):
    previous_arrears = rent.arrears
    rent_gale = rent.rentpa / rent.freq_id
    rent.arrears = previous_arrears + rent_gale
    return


# Arguments for next_rent_date: (rentid int, rentype int, periods int) RETURNS list of dates
def update_last_rent_date(rent):
    query = db.session.query(func.mjinn.next_rent_date(rent.id, 1, 1)).all()[0]
    for last_rent_date in query:
        rent.lastrentdate = last_rent_date
    return rent.lastrentdate


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

