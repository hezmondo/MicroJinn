import json
from app import db, cache
from flask import request
from flask_login import current_user
from sqlalchemy.orm import load_only
from app.dao.database import commit_to_database
from app.models import Agent, Case, Charge, ChargeType, Date_m, DocFile, DigFile, EmailAcc, FormLetter, Jstore, \
    Income, IncomeAlloc, Landlord, LeaseUpType, Loan, MoneyItem, Property, PrCharge, PrHistory, \
    Rent, RentExternal, MoneyAcc, TypeDeed, TypeDoc


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


def delete_record(item_id, item):
    id_2 = request.args.get('id_2')
    id_dict = {}
    redir = "rent_bp.rents_basic"
    if item == "agent":
        Agent.query.filter_by(id=item_id).delete()
        redir = "agent_bp.agents"
    elif item == "case":
        Case.query.filter_by(id=item_id).delete()
        redir = "rent_bp.rent"
    elif item == "charge":
        Charge.query.filter_by(id=item_id).delete()
        redir = "rent_bp.rent"
        id_dict = {"id": id_2}
    elif item == "doc":
        DocFile.query.filter_by(id=item_id).delete()
        redir = "doc_bp.docfiles"
    elif item == "dig":
        DigFile.query.filter_by(id=item_id).delete()
        redir = "doc_bp.docfiles"
    elif item == "email_acc":
        EmailAcc.query.filter_by(id=item_id).delete()
        redir = "util_bp.email_accs"
    elif item == "formletter":
        FormLetter.query.filter_by(id=item_id).delete()
        redir = "formletter_bp.forms"
    elif item == "income":
        Income.query.filter_by(id=item_id).delete()
        redir = "income_bp.income"
    elif item == "incomealloc":
        IncomeAlloc.query.filter_by(id=item_id).delete()
        redir = "income_bp.income"
    elif item == "landlord":
        Landlord.query.filter_by(id=item_id).delete()
        redir = "landlord_bp.landlords"
    elif item == "loan":
        Loan.query.filter_by(id=item_id).delete()
        redir = "loan_bp.loans"
    elif item == "money_acc":
        MoneyAcc.query.filter_by(id=item_id).delete()
        redir = "money_bp.moneyaccs"
    elif item == "money_item":
        MoneyItem.query.filter_by(id=item_id).delete()
        redir = "money_bp.money_items"
        id_dict = {"id": id_2}
    elif item == "pr_charge":
        PrCharge.query.filter_by(id=item_id).delete()
        redir = "pr_bp.pr_history"
    elif item == "property":
        Property.query.filter_by(id=item_id).delete()
        redir = "properties"
    elif item == "pr_file":
        PrHistory.query.filter_by(id=item_id).delete()
        redir = "pr_bp.pr_history"
        id_dict = {"rent_id": id_2}
    elif item == "rent":
        Rent.query.filter_by(id=item_id).delete()
    elif item == "rent_external":
        RentExternal.query.filter_by(id=item_id).delete()
    commit_to_database()
    return redir, id_dict


def delete_record_basic(item_id, item):
    if item == "case":
        Case.query.filter_by(id=item_id).delete()
    elif item == "charge":
        Charge.query.filter_by(id=item_id).delete()
    elif item == "pr_charge":
        PrCharge.query.filter_by(id=item_id).delete()
    elif item == "pr_file":
        PrHistory.query.filter_by(id=item_id).delete()


@cache.cached(key_prefix='db_charge_types_all')
def get_charge_types():
    charge_types = ChargeType.query.all()

    return charge_types


@cache.cached(key_prefix='db_dates_m_all')
def get_dates_m():
    dates_m = Date_m.query.with_entities(Date_m.code_id, Date_m.month, Date_m.day).all()

    return dates_m


def get_deed(deed_id):
    return TypeDeed.query.get(deed_id)


def get_deed_id(deedcode):
    deed = db.session.query(TypeDeed).filter_by(deedcode=deedcode).one()
    return deed.id


def get_deed_types():
    deed_types = TypeDeed.query.all()

    return deed_types


def get_doctype(doctype_id):   #returns desc as doctype
    return db.session.query(TypeDoc).filter_by(id=doctype_id).options(load_only('desc')).one_or_none()


@cache.cached(key_prefix='db_doc_types_all')
def get_doc_types():
    doc_types = TypeDoc.query.all()

    return doc_types


def get_filters(type):
    return Jstore.query.filter(Jstore.type == type).all()


def get_filter_stored(filtr_id):
    return db.session.query(Jstore).filter_by(id=filtr_id).options(load_only('content')).one_or_none()


def get_idlist_recent(type):
    try:
        id_list = json.loads(getattr(current_user, type))
    except (AttributeError, TypeError, ValueError):
        id_list = [1, 2, 3]

    return id_list


def pop_idlist_recent(type, id):
    id_list = get_idlist_recent(type)
    if id in id_list:
        id_list.remove(id)
    id_list.insert(0, id)
    if len(id_list) > 15:
        id_list.pop()
    setattr(current_user, type, json.dumps(id_list))
    commit_to_database()


def get_uplift_types():
    uplift_types = LeaseUpType.query.all()

    return uplift_types


def post_deed(deed_id, rent_id):
    if deed_id == 0:
        deed = TypeDeed()
    else:
        deed = TypeDeed.query.get(deed_id)
    deed.deedcode = request.form.get("deedcode")
    deed.nfee = request.form.get("nfee")
    deed.nfeeindeed = request.form.get("nfeeindeed")
    deed.info = request.form.get("info")
    db.session.add(deed)
    db.session.flush()
    deed_id = deed.id
    if rent_id != 0:
        rent = Rent.query.get(rent_id)
        rent.deed_id = deed_id
    commit_to_database()

    return deed_id


