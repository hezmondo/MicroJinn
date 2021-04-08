from app import app


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
    _names = ['in arrears', 'in advance']

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


class Date_m:
    _table = [
        # 2 rows for datecode_id == 1 or 2
        # each element is a tuple: (month, day to use)
        [(3, 25), (6, 24), (9, 29), (12, 25)],
        [(3, 31), (6, 30), (9, 30), (12, 31)]
    ]

    @staticmethod
    def get_dates(datecode_id):
        return Date_m._table[datecode_id - 1]


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


class RentType:
    # the "name" of the type of rent

    @staticmethod
    def rent_type(tenuredet):
        # note that we return a `.copy()`, if the caller changes the list it does not affect the list we have here
        return "rent charge" if tenuredet == "rentcharge" else "ground rent"


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


@app.context_processor
def inject_model_types():
    # this is called by Flask on every request
    # inject a dictionary of all the model types, so they are easily accessible in any template
    return {
        'AcTypes': AcTypes,
        'AdvArr': AdvArr,
        'BatchStatuses': BatchStatuses,
        'Date_m': Date_m,
        'Freqs': Freqs,
        'HrStatuses': HrStatuses,
        'MailTos': MailTos,
        'PayTypes': PayTypes,
        'PrDeliveryTypes': PrDeliveryTypes,
        'PropTypes': PropTypes,
        'RentType': RentType,
        'SaleGrades': SaleGrades,
        'Statuses': Statuses,
        'Tenures': Tenures,
    }
