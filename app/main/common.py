# common.py - attempt to put all commonly used non db stuff here and in functions.py
import json
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from app.dao.common import get_dates_m
from app.models import Jstore, Landlord, TypeDeed


class AcTypes:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ["autopay", "normal", "peppercorn", "reduced", "special"]

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return AcTypes._names.copy()

    @staticmethod
    def get_name(id):
        return AcTypes._names[id - 1]

    @staticmethod
    def get_id(name):
        return AcTypes._names.index(name) + 1


class AdvArr:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ['in advance', 'in arrears']

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return AdvArr._names.copy()

    @staticmethod
    def get_name(id):
        return AdvArr._names[id - 1]

    @staticmethod
    def get_id(name):
        return AdvArr._names.index(name) + 1


class BatchStatuses:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ['completed', 'pending']

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return BatchStatuses._names.copy()

    @staticmethod
    def get_name(id):
        return BatchStatuses._names[id - 1]

    @staticmethod
    def get_id(name):
        return BatchStatuses._names.index(name) + 1


class Freqs:
    # the "names" of the types
    _names = ["yearly", "half yearly", "quarterly", "monthly", "four weekly", "weekly"]
    # ids are really frequencies are per annum, 1--52
    # but are called "ids" for historical reasons
    # this list must be kept in same order as `_names` above
    _ids = [1, 2, 4, 12, 13, 52]
    assert len(_ids) == len(_names)

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return Freqs._names.copy()

    @staticmethod
    def get_name(id):
        index = Freqs._ids.index(id)
        return Freqs._names[index]

    @staticmethod
    def get_id(name):
        index = Freqs._names.index(name)
        return Freqs._ids[index]


class HrStatuses:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ["active", "dormant", "suspended", "terminated"]

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return HrStatuses._names.copy()

    @staticmethod
    def get_name(id):
        return HrStatuses._names[id - 1]

    @staticmethod
    def get_id(name):
        return HrStatuses._names.index(name) + 1


def get_idlist_recent(type):
    try:
        id_list = json.loads(getattr(current_user, type))
    except (AttributeError, TypeError, ValueError):
        id_list = [1, 2, 3]

    return id_list


class MailTos:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ['to agent', 'to tenantname care of agent', 'to tenantname at property','to owner or occupier at property']

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return MailTos._names.copy()

    @staticmethod
    def get_name(id):
        return MailTos._names[id - 1]

    @staticmethod
    def get_id(name):
        return MailTos._names.index(name) + 1


class PayTypes:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ["cheque", "bacs", "phone", "cash", "web"]

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return PayTypes._names.copy()

    @staticmethod
    def get_name(id):
        return PayTypes._names[id - 1]

    @staticmethod
    def get_id(name):
        return PayTypes._names.index(name) + 1


class PrDeliveryTypes:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ['email', 'post', 'email and post']

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return PrDeliveryTypes._names.copy()

    @staticmethod
    def get_name(id):
        return PrDeliveryTypes._names[id - 1]

    @staticmethod
    def get_id(name):
        return PrDeliveryTypes._names.index(name) + 1


class PropTypes:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ["commercial", "flat", "garage", "house", "land", "multiple"]

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return PropTypes._names.copy()

    @staticmethod
    def get_name(id):
        return PropTypes._names[id - 1]

    @staticmethod
    def get_id(name):
        return PropTypes._names.index(name) + 1


class SaleGrades:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ["for sale", "not for sale", "intervening title", "poor title"]

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return SaleGrades._names.copy()

    @staticmethod
    def get_name(id):
        return SaleGrades._names[id - 1]

    @staticmethod
    def get_id(name):
        return SaleGrades._names.index(name) + 1


class Statuses:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ["active", "case", "grouped", "managed", "new", "sold", "terminated", "x-ray"]

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return Statuses._names.copy()

    @staticmethod
    def get_name(id):
        return Statuses._names[id - 1]

    @staticmethod
    def get_id(name):
        return Statuses._names.index(name) + 1


class Tenures:
    # the "names" of the types
    # ids are index into these, counting from 1
    _names = ['freehold', 'leasehold', 'rentcharge']

    @staticmethod
    def names():
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return Tenures._names.copy()

    @staticmethod
    def get_name(id):
        return Tenures._names[id - 1]

    @staticmethod
    def get_id(name):
        return Tenures._names.index(name) + 1


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
