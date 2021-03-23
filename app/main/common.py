# common.py - attempt to put all commonly used non db stuff here and in functions.py
from dateutil.relativedelta import relativedelta
from app.dao.common import get_dates_m, AcTypes, AdvArr, Freqs, MailTos, PrDeliveryTypes, SaleGrades, Statuses, Tenures
from app.models import Jstore, Landlord, TypeDeed


def get_combodict_basic():
    # combobox values for headrent and rent, without "all" as an option
    actypes = AcTypes.names()
    advars = AdvArr.names()
    freqs = Freqs.names()
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    tenures = Tenures.names()
    combo_dict = {
        "actypes": actypes,
        "advars": advars,
        "freqs": freqs,
        "landlords": landlords,
        "tenures": tenures,
    }
    return combo_dict


def get_combodict_rent():
    # add the values unique to rent
    combo_dict = get_combodict_basic()
    deedcodes = [value for (value,) in TypeDeed.query.with_entities(TypeDeed.deedcode).all()]
    combo_dict['deedcodes'] = deedcodes
    combo_dict['mailtos'] = MailTos.names()
    combo_dict['prdeliveries'] = PrDeliveryTypes.names()
    combo_dict['salegrades'] = SaleGrades.names()
    combo_dict['statuses'] = Statuses.names()

    return combo_dict


def get_combodict_filter():
    # use the full rent combodict and insert "all values" for the filter functions, plus offer "options"
    combo_dict = get_combodict_rent()
    combo_dict['actypes'].insert(0, "all actypes")
    combo_dict['landlords'].insert(0, "all landlords")
    combo_dict['prdeliveries'].insert(0, "all prdeliveries")
    combo_dict['salegrades'].insert(0, "all salegrades")
    combo_dict['statuses'].insert(0, "all statuses")
    combo_dict['tenures'].insert(0, "all tenures")
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

    return date2


def inc_date_m(date1, frequency, datecode_id, periods):
    # first we get a new pure date calculated forwards or backwards for the number of periods
    date2 = inc_date(date1, frequency, periods)
    # now get special date sequences from date_m table
    dates_m = get_dates_m()
    if datecode_id != 0:
        for item in dates_m:
            if item[0] == datecode_id and item[1] == date2.month:
                date2 = date2.replace(day=item[2])

    return date2
