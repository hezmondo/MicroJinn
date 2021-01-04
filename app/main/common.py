# common.py - attempt to put all commonly used stuff here and in functions.py
import json
import os
from app import db
from flask_login import current_user, login_required
from app.models import Jstore, Landlord, Typeactype, Typeadvarr, Typedeed, Typefreq, Typemailto, Typeprdelivery, \
                        Typesalegrade, Typestatus, Typetenure\


# common functions
def get_combodict(type):
    # first gather  values for comboboxes used for the rent object, without "all" as an option
    actypes = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    advars = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    freqs = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    mailtos = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    prdeliveries = [value for (value,) in Typeprdelivery.query.with_entities(Typeprdelivery.prdeliverydet).all()]
    salegrades = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]
    statuses = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenures = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]
    options = ("include", "exclude", "only")

    combo_dict = {
        "actypes": actypes,
        "advars": advars,
        "deedcodes": deedcodes,
        "freqs": freqs,
        "landlords": landlords,
        "mailtos": mailtos,
        "prdeliveries": prdeliveries,
        "salegrades": salegrades,
        "statuses": statuses,
        "tenures": tenures,
        "options": options
    }
    if type == "enhanced":
        # add "all" as an option for filters allowing selection of more than one value
        actypes.insert(0, "all actypes")
        landlords.insert(0, "all landlords")
        prdeliveries.insert(0, "all prdeliveries")
        salegrades.insert(0, "all salegrades")
        statuses.insert(0, "all statuses")
        tenures.insert(0, "all tenures")
        filternames = [value for (value,) in Jstore.query.with_entities(Jstore.code).all()]
        combo_dict["filternames"] = filternames
        combo_dict["filtertypes"] = ("payrequest", "rentprop", "income")

    return combo_dict


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
