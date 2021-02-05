# common.py - attempt to put all commonly used stuff here and in functions.py
import json
import os
from app import db
from flask import request
from flask_login import current_user, login_required
from app.models import Agent, Jstore, Landlord, Typeactype, Typeadvarr, Typedeed, Typefreq, Typemailto, \
                        Typeprdelivery, Typesalegrade, Typestatus, Type_status_hr, Typetenure\


# common functions
def get_combodict_basic():
    # combobox values for headrent and rent, without "all" as an option
    actypes = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    advars = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqs = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    tenures = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]

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
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    mailtos = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    prdeliveries = [value for (value,) in Typeprdelivery.query.with_entities(Typeprdelivery.prdeliverydet).all()]
    salegrades = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]
    statuses = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
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


def get_hr_statuses():
    hr_statuses = [value for (value,) in Type_status_hr.query.with_entities(Type_status_hr.hr_status).all()]
    # hr_statuses = ["active", "dormant", "suspended", "terminated"]

    return hr_statuses


def get_idlist_recent(type):
    id_list = [1, 51, 101, 151, 201, 251, 301, 351, 401, 451, 501]
    id_list = json.loads(getattr(current_user, type)) if getattr(current_user, type) else id_list

    return id_list


def pop_idlist_recent(type, id):
    id_list = json.loads(getattr(current_user, type))
    if id not in id_list:
        id_list.insert(0, id)
        if len(id_list) > 30:
            id_list.pop()
        setattr(current_user, type, json.dumps(id_list))
        db.session.commit()


def get_postvals_id():
    # returns the post values for rent and head rent as dict with class id generated for combobox value
    postvals_id = {
        "actype": "",
        "advarr": "",
        "agent": "",
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
        if actval and actval != "":
            if key == "actype":
                actval = Typeactype.query.with_entities(Typeactype.id).filter(Typeactype.actypedet == actval).one()[0]
            elif key == "advarr":
                actval = Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == actval).one()[0]
            elif key == "agent":
                actval = Agent.query.with_entities(Agent.id).filter(Agent.detail == actval).one()[0]
            elif key == "deedtype":
                actval = Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == actval).one()[0]
            elif key == "frequency":
                actval = Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == actval).one()[0]
            elif key == "landlord":
                actval = Landlord.query.with_entities(Landlord.id).filter(Landlord.name == actval).one()[0]
            elif key == "mailto":
                actval = Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == actval).one()[0]
            elif key == "salegrade":
                actval = Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == actval).one()[0]
            elif key == "status":
                actval = Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == actval).one()[0]
            elif key == "tenure":
                actval = Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == actval).one()[0]
            postvals_id[key] = actval
            print(key, value)

    return postvals_id

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
