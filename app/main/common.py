# common.py - attempt to put all commonly used non db stuff here and in functions.py
import json
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from app.dao.common import get_dates_m
from app.models import Jstore, Landlord, TypeDeed


def get_actype(actype_id):
    if actype_id == 1:
        return "autopay"
    elif actype_id == 2:
        return "normal"
    elif actype_id == 3:
        return "peppercorn"
    elif actype_id == 4:
        return "reduced"
    else:
        return "special"


def get_actype_id(actype):
    if actype == "autopay":
        return 1
    elif actype == "normal":
        return 2
    elif actype == "peppercorn":
        return 3
    elif actype == "reduced":
        return 4
    else:
        return 5


def get_actypes():
    return ["autopay", "normal", "peppercorn", "reduced", "special"]


def get_advarrdet(advarr_id):

    return "in advance" if advarr_id == 1 else "in arrears"


def get_advarr_id(advarrdet):

    return 1 if advarrdet == "in advance" else 2


def get_advarr_types():

    return ['in advance', 'in arrears']


def get_batchstatus(status_id):

    return "completed" if status_id == 1 else "pending"


def get_batchstatus_id(status):

    return 1 if status == "completed" else 2


def get_batchstatus_types():

    return ['completed', 'pending']


def get_combodict_basic():
    # combobox values for headrent and rent, without "all" as an option
    actypes = get_actypes()
    advars = get_advarr_types()
    freqs = get_freqs()
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    tenures = get_tenures()
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
    combo_dict['mailtos'] = get_mailto_types()
    combo_dict['prdeliveries'] = get_prdelivery_types()
    combo_dict['salegrades'] = get_salegrades()
    combo_dict['statuses'] = get_statuses()

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


def get_freq(freq_id):
    if freq_id == 1:
        return "yearly"
    elif freq_id == 2:
        return "half yearly"
    elif freq_id == 4:
        return "quarterly"
    elif freq_id == 12:
        return "monthly"
    elif freq_id == 13:
        return "four weekly"
    else:
        return "weekly"


def get_freq_id(freq):
    if freq == "yearly":
        return 1
    elif freq == "half yearly":
        return 2
    elif freq == "quarterly":
        return 4
    elif freq == "monthly":
        return 12
    elif freq == "four weekly":
        return 13
    else:
        return 52


def get_freqs():
    return ["yearly", "half yearly", "quarterly", "monthly", "four weekly", "weekly"]




def get_hr_status(status_id):
    if status_id == 1:
        return "active"
    elif status_id == 2:
        return "dormant"
    elif status_id == 3:
        return "suspended"
    else:
        return "terminated"


def get_hr_statuses():

    return ["active", "dormant", "suspended", "terminated"]


def get_hr_status_id(status):
    if status == "active":
        return 1
    elif status == "dormant":
        return 2
    elif status == "suspended":
        return 3
    else:
        return 4


def get_idlist_recent(type):
    try:
        id_list = json.loads(getattr(current_user, type))
    except (AttributeError, TypeError, ValueError):
        id_list = [1, 2, 3]

    return id_list


def get_mailtodet(mailto_id):
    if mailto_id == 1:
        return "to agent"
    elif mailto_id == 2:
        return "to tenant name care of agent"
    elif mailto_id == 3:
        return "to tenant name at property"
    else:
        return "to owner or occupier at property"


def get_mailto_id(mailtodet):
    if mailtodet == "to agent":
        return 1
    elif mailtodet == "to tenant name care of agent":
        return 2
    elif mailtodet == "to tenant name at property":
        return 3
    else:
        return 4


def get_mailto_types():
    return ['to agent', 'to tenantname care of agent', 'to tenantname at property','to owner or occupier at property']


def get_paytype(paytype_id):
    if paytype_id == 1:
        return "cheque"
    elif paytype_id == 2:
        return "bacs"
    elif paytype_id == 3:
        return "phone"
    elif paytype_id == 4:
        return "cash"
    else:
        return "web"


def get_paytype_id(paytype):
    if paytype == "cheque":
        return 1
    elif paytype == "bacs":
        return 2
    elif paytype == "phone":
        return 3
    elif paytype == "cash":
        return 4
    else:
        return 5


def get_paytypes():
    return ["cheque", "bacs", "phone", "cash", "web"]


def get_prdelivery(prdelivery_id=1):
    if prdelivery_id == 1:
        return "email"
    elif prdelivery_id == 2:
        return "post"
    else:
        return "email and post"


def get_prdelivery_id(prdelivery='email'):
    if prdelivery == "email":
        return 1
    elif prdelivery == "post":
        return 2
    else:
        return 3


def get_prdelivery_types():

    return ['email', 'post', 'email and post']


def get_proptype(proptype_id):
    if proptype_id == 1:
        return "commercial"
    elif proptype_id == 2:
        return "flat"
    elif proptype_id == 3:
        return "garage"
    elif proptype_id == 4:
        return "house"
    elif proptype_id == 5:
        return "land"
    else:
        return "multiple"


def get_proptype_id(proptype):
    if proptype == "commercial":
        return 1
    elif proptype == "flat":
        return 2
    elif proptype == "garage":
        return 3
    elif proptype == "house":
        return 4
    elif proptype == "land":
        return 5
    else:
        return 6


def get_proptypes():
    return ["commercial", "flat", "garage", "house", "land", "multiple"]


def get_salegrade(salegrade_id):
    if salegrade_id == 1:
        return "for sale"
    elif salegrade_id == 2:
        return "not for sale"
    elif salegrade_id == 3:
        return "intervening title"
    else:
        return "poor title"


def get_salegrade_id(salegrade):
    if salegrade == "for sale":
        return 1
    elif salegrade == "not for sale":
        return 2
    elif salegrade == "intervening title":
        return 3
    else:
        return 4


def get_salegrades():
    return ["for sale", "not for sale", "intervening title", "poor title"]


def get_status(status_id):
    if status_id == 1:
        return "active"
    elif status_id == 2:
        return "case"
    elif status_id == 3:
        return "grouped"
    elif status_id == 4:
        return "managed"
    elif status_id == 5:
        return "new"
    elif status_id == 6:
        return "sold"
    elif status_id == 7:
        return "terminated"
    else:
        return "x-ray"


def get_status_id(status):
    if status == "active":
        return 1
    elif status == "case":
        return 2
    elif status == "grouped":
        return 3
    elif status == "managed":
        return 4
    elif status == "new":
        return 5
    elif status == "sold":
        return 6
    elif status == "terminated":
        return 7
    else:
        return 8


def get_statuses():
    return ["active", "case", "grouped", "managed", "new", "sold", "terminated", "x-ray"]


def get_tenure(tenure_id=1):
    if tenure_id == 1:
        return "freehold"
    elif tenure_id == 2:
        return "leasehold"
    else:
        return "rentcharge"


def get_tenure_id(tenure='freehold'):
    if tenure == "freehold":
        return 1
    elif tenure == "leasehold":
        return 2
    else:
        return 3

def get_tenures():

    return ['freehold', 'leasehold', 'rentcharge']


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

