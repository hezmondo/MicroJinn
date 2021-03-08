# common.py - attempt to put all commonly used non db stuff here and in functions.py
import json
import datetime

from dateutil.relativedelta import relativedelta
from flask import request
from flask_login import current_user
from app.models import Agent, Jstore, Landlord, TypeAcType, TypeAdvArr, TypeDeed, TypeFreq, TypeMailTo, \
                        TypePrDelivery, TypeSaleGrade, TypeStatus, TypeStatusHr, TypeTenure


def get_combodict_basic():
    # combobox values for headrent and rent, without "all" as an option
    actypes = [value for (value,) in TypeAcType.query.with_entities(TypeAcType.actypedet).all()]
    advars = [value for (value,) in TypeAdvArr.query.with_entities(TypeAdvArr.advarrdet).all()]
    freqs = [value for (value,) in TypeFreq.query.with_entities(TypeFreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    tenures = [value for (value,) in TypeTenure.query.with_entities(TypeTenure.tenuredet).all()]

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
    mailtos = [value for (value,) in TypeMailTo.query.with_entities(TypeMailTo.mailtodet).all()]
    prdeliveries = [value for (value,) in TypePrDelivery.query.with_entities(TypePrDelivery.prdeliverydet).all()]
    salegrades = [value for (value,) in TypeSaleGrade.query.with_entities(TypeSaleGrade.salegradedet).all()]
    statuses = [value for (value,) in TypeStatus.query.with_entities(TypeStatus.statusdet).all()]
    combo_dict['deedcodes'] = deedcodes
    combo_dict['mailtos'] = mailtos
    combo_dict['prdeliveries'] = prdeliveries
    combo_dict['salegrades'] = salegrades
    combo_dict['statuses'] = statuses

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
    combo_dict['options'] = ("include", "exclude", "only")
    filternames = [value for (value,) in Jstore.query.with_entities(Jstore.code).all()]
    combo_dict["filternames"] = filternames
    combo_dict["filtertypes"] = ("payrequest", "rentprop", "income")

    return combo_dict


def inc_date_m(date1, frequency, datecode_id, periods):
    # first we get a new pure date calculated forwards or backwards for the number of periods
    date2 = inc_date(date1, frequency, periods)
    dates = [(1, 3, 25), (1, 6, 24), (1, 9, 29), (1, 12, 25), (2, 6, 30), (2, 12, 31), (3, 3, 31), (3, 9, 30),
             (4, 3, 31), (4, 6, 30), (4, 9, 30), (4, 12, 31)]
    if datecode_id != 0:
        for item in dates:
            if item[0] == datecode_id and item[1] == date2.month:
                date2 = date2.replace(day=item[2])

    return date2


def get_hr_statuses():
    hr_statuses = [value for (value,) in TypeStatusHr.query.with_entities(TypeStatusHr.hr_status).all()]
    # hr_statuses = ["active", "dormant", "suspended", "terminated"]

    return hr_statuses


def get_idlist_recent(type):
    try:
        id_list = json.loads(getattr(current_user, type))
    except (AttributeError, TypeError, ValueError):
        id_list = [1, 2, 3]

    return id_list


def get_postvals_id():
    # returns the post values for rent and head rent as dict with class id generated for combobox value
    postvals_id = {
        "actype": "",
        "advarr": "",
        "agent": "",
        "deedcode": "",
        "frequency": "",
        "landlord": "",
        "mailto": "",
        "prdelivery": "",
        "salegrade": "",
        "status": "",
        "tenure": ""
    }
    for key, value in postvals_id.items():
        actval = request.form.get(key)
        if actval and actval != "" and actval!= "None":
            if key == "actype":
                actval = TypeAcType.query.with_entities(TypeAcType.id).filter(TypeAcType.actypedet == actval).one()[0]
            elif key == "advarr":
                actval = TypeAdvArr.query.with_entities(TypeAdvArr.id).filter(TypeAdvArr.advarrdet == actval).one()[0]
            elif key == "agent":
                actval = Agent.query.with_entities(Agent.id).filter(Agent.detail == actval).one()[0]
            elif key == "deedcode":
                actval = TypeDeed.query.with_entities(TypeDeed.id).filter(TypeDeed.deedcode == actval).one()[0]
            elif key == "frequency":
                actval = TypeFreq.query.with_entities(TypeFreq.id).filter(TypeFreq.freqdet == actval).one()[0]
            elif key == "landlord":
                actval = Landlord.query.with_entities(Landlord.id).filter(Landlord.name == actval).one()[0]
            elif key == "mailto":
                actval = TypeMailTo.query.with_entities(TypeMailTo.id).filter(TypeMailTo.mailtodet == actval).one()[0]
            elif key == "prdelivery":
                actval = TypePrDelivery.query.with_entities(TypePrDelivery.id).filter(TypePrDelivery.prdeliverydet == actval).one()[0]
            elif key == "salegrade":
                actval = TypeSaleGrade.query.with_entities(TypeSaleGrade.id).filter(TypeSaleGrade.salegradedet == actval).one()[0]
            elif key == "status":
                actval = TypeStatus.query.with_entities(TypeStatus.id).filter(TypeStatus.statusdet == actval).one()[0]
            elif key == "tenure":
                actval = TypeTenure.query.with_entities(TypeTenure.id).filter(TypeTenure.tenuredet == actval).one()[0]
            postvals_id[key] = actval
            print(key, value)

    return postvals_id


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


def inc_rent_date(date1, date_id, freq, num):
    # this function increments or decrements a date by num periods and then modulates the day of month
    date2 = inc_date(date1, freq, num)

    return date2


# def preferredEncoding() -> str:
#     # return the OS preferred encoding to use for text, e.g. when reading/writing from/to a text file via pathlib.open()
#     # ("utf-8" for Linux, "cp1252" for Windows)
#     import locale
#     return locale.getpreferredencoding()
#
#
# def readFromFile(filename):
#     basedir = os.path.abspath(os.path.dirname('mjinn'))
#     mergedir = os.path.join(basedir, 'app/templates/mergedocs')
#     filePath = os.path.join(mergedir, filename)
#     # with open(htmlFilePath, "r" encoding="utf-8") as f:
#     #     htmlText = f.read()
#     with filePath.open('r', encoding="utf-8") as f:
#         fileText = f.read()
#     return fileText
