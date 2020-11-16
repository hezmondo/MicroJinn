# common.py - attempt to put all commonly used stuff here
import os
from app.models import Landlord, Typeadvarr, Typefreq, Typestatus, Typetenure\


# common functions
def get_combos_common():
    # This function returns values for comboboxes used by rents, queries and headrents
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.landlordname).all()]
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenuredets = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]

    return advarrdets, freqdets, landlords, statusdets, tenuredets


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
