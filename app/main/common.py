# common.py - attempt to put all commonly used non db stuff here and in functions.py
import typing
from flask import current_app, json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app import app
from app.main.functions import money
from app.models import Jstore, TypeDeed
from app.modeltypes import Date_m
from app.dao.common import add_new_recent_search, delete, get_recent_searches_asc, \
    commit_to_database


# convert a string so that the first letter is uppercase
@app.context_processor
def string_processor():
    def upper_first(string):
        return string[0].upper() + string[1:]

    return dict(upper_first=upper_first)


def get_combodict_rent():
    # add the values unique to rent
    combo_dict = {}
    deedcodes = [value for (value,) in TypeDeed.query.with_entities(TypeDeed.deedcode).all()]
    combo_dict['deedcodes'] = deedcodes

    return combo_dict


def get_combodict_filter():
    # use the full rent combodict and insert "all values" for the filter functions, plus offer "options"
    combo_dict = get_combodict_rent()
    # combo_dict['landlords'].insert(0, "all landlords")
    combo_dict['options'] = ["include", "exclude", "only"]
    filternames = [value for (value,) in Jstore.query.with_entities(Jstore.code).all()]
    combo_dict["filternames"] = filternames
    combo_dict["filtertypes"] = ["payrequest", "rentprop", "income"]

    return combo_dict


def mpost_search(fdict, type):
    recent_searches = get_recent_searches_asc(type)
    # convert fdict into a string, as this is how it is saved in the db
    str_dict = json.dumps(fdict)
    # If the search dict already exists in the table we replace it so it becomes the most recent search
    for recent_search in recent_searches:
        if str_dict == recent_search.dict:
            delete(recent_search)
    # If there are already 6 records in the table we delete the oldest
    if len(recent_searches) >= 6:
        first_record = recent_searches[0]
        delete(first_record)
    add_new_recent_search(fdict, type)
    commit_to_database()


def get_rents_fdict(action='basic'):
    # get simple filter dictionary for rents and rents external pages
    dict_basic = {
        "rentcode": "",
        "agent": "",
        "propaddr": "",
        "source": "",
        "tenantname": ""
    }
    # add advanced filter keys for advanced queries and payrequest pages
    dict_plus = {
        "actype": ["all actypes"],
        "agentmailto": "include",
        "arrears": "",
        "charges": "include",
        "emailable": "include",
        "enddate": "",
        "landlord": ["all landlords"],
        "prdelivery": ["all prdeliveries"],
        "rentpa": "",
        "rentperiods": "",
        "runsize": "",
        "salegrade": ["all salegrades"],
        "status": ["all statuses"],
        "tenure": ["all tenures"]
    }
    return dict_basic if action in ("basic", "external") else dict_plus


def inc_date(date1, freq, num):
    # this function simply increments or decrements a date by num periods without modulating day of month
    date2 = date1
    if freq == 1:
        date2 = date1 + relativedelta(years=num)
    elif freq == 2:
        date2 = date1 + relativedelta(months=num * 6)
    elif freq == 4:
        date2 = date1 + relativedelta(months=num * 3)
    elif freq == 12:
        date2 = date1 + relativedelta(months=num)
    elif freq == 13:
        date2 = date1 + relativedelta(weeks=num * 4)
    elif freq == 52:
        date2 = date1 + relativedelta(weeks=num)
    else:
        current_app.logger.warn(f"inc_date(): Unexpected 'freq' ({freq})")

    return date2


def inc_date_m(date1, frequency, datecode_id, periods):
    # first we get a new pure date calculated forwards or backwards for the number of periods
    date2 = inc_date(date1, frequency, periods)
    if datecode_id != 0:
        if frequency not in (2, 4):
            current_app.logger.warn(f"inc_date_m(): Unexpected 'frequency' ({frequency})")
        # now get special date sequences from date_m model type
        dates_m = Date_m.get_dates(datecode_id)
        for item in dates_m:
            if item[0] == date2.month:
                return date2.replace(day=item[1])
        current_app.logger.warn(f"inc_date_m(): Unexpected 'date2' ({date2})")

    return date2


@app.context_processor
def date_processor():
    def next_rent_date(date1, frequency, datecode_id, periods):
        # first we get a new pure date calculated forwards or backwards for the number of periods
        date2 = inc_date(date1, frequency, periods)
        if datecode_id and datecode_id != 0:
            if frequency not in (2, 4):
                current_app.logger.warn(f"inc_date_m(): Unexpected 'frequency' ({frequency})")
            # now get special date sequences from date_m model type
            dates_m = Date_m.get_dates(datecode_id)
            for item in dates_m:
                if item[0] == date2.month:
                    return date2.replace(day=item[1])
            current_app.logger.warn(f"inc_date_m(): Unexpected 'date2' ({date2})")

        return date2

    return dict(next_rent_date=next_rent_date)


@app.context_processor
def date_processor():
    def relative_delta(date, days):
        date2 = date + relativedelta(days=days)

        return date2

    return dict(relative_delta=relative_delta)


# @app.context_processor
# def utility_processor():
#     def format_price(amount, currency=u'€'):
#         return u'{0:.2f}{1}'.format(amount, currency)
#     return dict(format_price=format_price)


@app.context_processor
def money_processor():
    def money_str(val: typing.Any, commas: bool = True, pound: bool = False) -> str:
        # Given a value which is a monetary amount (e.g. as returned by `money()` above, though we call that for you)
        # return it as a string
        # by default the string does have comma-separators and does not have a leading £ symbol, e.g. 12,345.67
        # value of `None` returns an empty string
        if val is None:
            return ""
        val = money(val)
        sVal = "{:,.2f}".format(val) if commas else "{:.2f}".format(val)
        if pound:
            sVal = "£" + sVal
        return sVal

    return dict(money_str=money_str)
