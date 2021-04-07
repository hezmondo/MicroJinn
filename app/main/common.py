# common.py - attempt to put all commonly used non db stuff here and in functions.py
from flask import current_app
from dateutil.relativedelta import relativedelta
from app.models import Jstore, TypeDeed
from app.modeltypes import Date_m


def get_combodict_rent():
    # add the values unique to rent
    combo_dict = {}
    deedcodes = [value for (value,) in TypeDeed.query.with_entities(TypeDeed.deedcode).all()]
    combo_dict['deedcodes'] = deedcodes

    return combo_dict


def get_combodict_filter():
    # use the full rent combodict and insert "all values" for the filter functions, plus offer "options"
    combo_dict = get_combodict_rent()
    combo_dict['landlords'].insert(0, "all landlords")
    combo_dict['options'] = ["include", "exclude", "only"]
    filternames = [value for (value,) in Jstore.query.with_entities(Jstore.code).all()]
    combo_dict["filternames"] = filternames
    combo_dict["filtertypes"] = ["payrequest", "rentprop", "income"]

    return combo_dict


def get_rents_fdict(action='basic'):
    # get simple filter dictionary for rents and rents external pages
    dict_basic = {
        "rentcode": "",
        "agentdetail": "",
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
        date2 = date1 + relativedelta(months=num*6)
    elif freq == 4:
        date2 = date1 + relativedelta(months=num*3)
    elif freq == 12:
        date2 = date1 + relativedelta(months=num)
    elif freq == 13:
        date2 = date1 + relativedelta(weeks=num*4)
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
