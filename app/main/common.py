# common.py - attempt to put all commonly used stuff here

import os

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
