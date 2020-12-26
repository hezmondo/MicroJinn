# common.py - attempt to put all commonly used stuff here
import os
from app.models import Jstore, Landlord, Typeactype, Typeadvarr, Typedeed, Typefreq, Typemailto, Typeprdelivery, \
                        Typesalegrade, Typestatus, Typetenure\


# common functions
def get_combodict(type):
    # first gather  values for comboboxes used for the rent object, without "all" as an option
    actypedets = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    mailtodets = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    prdeliverydets = [value for (value,) in Typeprdelivery.query.with_entities(Typeprdelivery.prdeliverydet).all()]
    salegradedets = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenuredets = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]
    options = ("include", "exclude", "only")

    combo_dict = {
        "actypedets": actypedets,
        "advarrdets": advarrdets,
        "deedcodes": deedcodes,
        "freqdets": freqdets,
        "landlords": landlords,
        "mailtodets": mailtodets,
        "prdeliverydets": prdeliverydets,
        "salegradedets": salegradedets,
        "statusdets": statusdets,
        "tenuredets": tenuredets,
        "options": options
    }
    if type == "enhanced":
        # add "all" as an option to allow this choice in certain filters
        actypedets.insert(0, "all actypes")
        # advarrdets.insert(0, "all advarrdets")
        # deedcodes.insert(0, "all deedcodes")
        # freqdets.insert(0, "all freqdets")
        landlords.insert(0, "all landlords")
        # mailtodets.insert(0, "all mailtodets")
        prdeliverydets.insert(0, "all prdeliverdets")
        salegradedets.insert(0, "all salegradedets")
        statusdets.insert(0, "all statuses")
        tenuredets.insert(0, "all tenures")
        filternames = [value for (value,) in Jstore.query.with_entities(Jstore.code).all()]
        combo_dict["filternames"] = filternames

    return combo_dict


def preferredEncoding() -> str:
    # return the OS preferred encoding to use for text, e.g. when reading/writing from/to a text file via pathlib.open()
    # ("utf-8" for Linux, "cp1252" for Windows)
    import locale
    return locale.getpreferredencoding()


def readFromFile(filename):
    basedir = os.path.abspath(os.path.dirname('mjinn'))
    mergedir = os.path.join(basedir, 'app/templates/mergedocs')
    filePath = os.path.join(mergedir, filename)
    # with open(htmlFilePath, "r" encoding="utf-8") as f:
    #     htmlText = f.read()
    with filePath.open('r', encoding="utf-8") as f:
        fileText = f.read()
    return fileText
