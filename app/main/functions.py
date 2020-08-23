import logging
import re
import hashlib
import datetime
import typing
import decimal
from app import db
from flask import abort
from sqlalchemy import exc
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_DOWN, ROUND_UP
from xhtml2pdf import pisa             # import python module
from app.main.exceptions import RentIntegerException


dbLogger = logging.getLogger("dbLogger")


def backup_database():
    """A  function to backup the mjinn database and
       handle exceptions if encountered"""
    dbLogger.info('Committing changes to db...')
    return
    # try:
    #     pass


def commit_to_database():
    """A shared function to make a commit to the database and
       handle exceptions if encountered"""
    dbLogger.info('Committing changes to db...')
    try:
        db.session.commit()
    except AssertionError as err:
        db.session.rollback()
        abort(409, err)
    except (exc.IntegrityError) as err:
        db.session.rollback()
        abort(409, err.orig)
    except Exception as err:
        db.session.rollback()
        abort(500, err)


def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")
    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result
    # close output file
    result_file.close()                 # close output file
    # return False on success and True on errors
    return pisa_status.err


def update_agent_recent():
    # mylist = curr.recent_agents
    return


def hashCode(rentcode):
    salt = "230498slkdfn348975ejhsoadjflkj"
    code = rentcode
    encodestring = salt + code
    hash_object = hashlib.sha1(encodestring.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return (hex_dig[0:6])

#
#   date and formatting functions
#

def dateToStr(date):
    # convert a datetime.date to a string in UK format
    # date of `None` returns an empty string
    if date is None:
        return ""
    return date.strftime("%d-%b-%Y")


def strToDate(date: str) -> typing.Union[datetime.date, None]:
    # convert a string to a datetime.date
    # always uses UK format
    # Note that this function *only* accepts a full date (4-digit-year)
    # and raises an exeception if converting fails
    # it is suitable for a string which is known to be a good, full date, e.g. returned from `dateToStr()` above
    # use `parseDataSoft()` or similar if you want a more forgiving conversion
    # string of `None`/empty returns `None`
    if str is None or str == "":
        return None
    return datetime.datetime.strptime(date, UkDateFormat).date()


def strToInt(string: str) -> typing.Union[int, None]:
    if string.strip() == "":
        return None
    else:
        return int(string)


def strToDec(string: str) -> Decimal:
    # Convert a string to a Decimal
    # Will still return an error if a non numerical string is passed
    # but changes empty strings to 0 conveniently
    # also removes commas, so that our "pretty-printed" numbers like "12,345.67" convert correctly
    if string.strip() == "":
        return Decimal(0)
    else:
        return Decimal(string.replace(",", ""))


def money(val: typing.Any, rounding: str=None) -> Decimal:
    # Return a "monetary amount" for a value
    # value can be any type accepted by the `Decimal()` constructor (e.g. Decimal, float, string)
    # A monetary amount has fixed 2 decimal places
    # Note that this is just a function returning a Decimal
    # We do not try to define Money as a subclass of Decimal to provide this
    # as that really requires a lot of work to get it right,
    # e.g. all operators must be overridden to return Money instead of Decimal, etc.
    #
    # Note also: we (deliberately) do not supply a `ROUND_...` default for `rounding`
    # Decimal.quantize() without supplying an explicit `rounding`
    # defaults to (decimal.DefaultContext) `ROUND_HALF_EVEN`
    # which means that 1.125 -> 1.12 but 1.135 -> 1.14
    # Old code seemed so "flaky"/inconsistent wrt when/how it rounded what
    # *but* seemed to work OK wherever it was used
    # so, for right or for wrong, I have tried to leave it "as-was"
    return Decimal(val).quantize(Decimal('0.01'), rounding)


def moneyToStr(val: typing.Any, commas: bool=True, pound: bool=False) -> str:
    # Given a value which is a monetary amount (e.g. as returned by `money()` above, though we call that for you)
    # return it as a string
    # by default the string does have comma-separators and does not have a leading £ symbol, e.g. 12,345.67
    # value of `None` returns an empty string
    if val is None:
        return ""
    val = money(val)
    sVal = "{:,.2f}".format(val) if commas else "{:.2f}".format(val)
    if pound:
        sVal = "£" + sVal
    return sVal


def strToMoney(string: str) -> Decimal:
    # Convert a string to a monetary amount
    # Will still return an error if a non numerical string is passed
    # but changes empty strings to 0 conveniently
    # also removes commas, and leading `£`, so that our "pretty-printed" numbers like "£12,345.67" convert correctly
    string = string.strip()
    if string.startswith("£"):
        string = string[1:]
    if string == "":
        return money(0)
    else:
        return money(string.replace(",", ""))


def truncateString(string: str, length: int) -> str:
    return string if string is None or len(string) <= length else string[0:length - 3] + '…'


def extractRentCodeStub(rentCode):
    rentCodeRegex = re.search("^(?P<stub>[a-zA-Z]+)", rentCode)
    return rentCodeRegex.group("stub")


def splitAddressPostcode(address: str) -> typing.List[str]:
    # Regex to separate postcode from the rest of an address,
    # returns a list with two elements: [first part of address, postcode]
    # Note: I inherited the regular expression written this way
    # it *assumes* the postcode will comes at the end, with nothing else after it
    # it could be "fooled" by having something like a postocde in the middle of an address
    # but I'm leaving it as-is
    parts = re.split(r'(\b[A-Z]{1,2}[0-9][A-Z0-9]? +[0-9][ABD-HJLNP-UW-Z]{2}\b)', address, flags=re.IGNORECASE)
    return parts


# def parseDateHard(date: str, parent=None) -> typing.Union[datetime.date, None]:
#     # converts a str (D/M/Y) to a datetime.date
#     # with an ErrorMsgBox() if str not a valid date
#     # None => str not a valid date
#     pyDate = parseDateSoft(date)
#     # if pyDate is None:
#     #     from widgets.messageboxes import ErrorMsgBox
#     #     ErrorMsgBox("Date '{}' not in correct format.\nLooking for D/M/Y".format(date), parent).exec()
#     #     return None
#     return pyDate


# def parseDateSoft(date: str) -> typing.Union[datetime.date, None]:
#     # converts a str (D/M/Y) to a datetime.date
#     # None => str not a valid date
#     try:
#         return datetime.datetime.strptime(date, UkDateFormat).date()
#     except ValueError:
#         try:
#             return datetime.datetime.strptime(date, UkDateFormatYear2).date()
#         except ValueError:
#             return None


# def isValidFullDateStr(date: str) -> bool:
#     return re.fullmatch(r"\d\d?/\d\d?/\d\d\d\d", date) is not None


def isValidDecimal(inputText) -> bool:
    try:
        decimal.Decimal(inputText)
        return True
    except decimal.InvalidOperation:
        return False


def isValidInt(inputText) -> bool:
    try:
        int(inputText)
        return True
    except ValueError:
        return False
#
# -    HTML functions
#
def appendHtmlFragmentToHtmlDocument(htmlDocument: str, htmlFragment: str) -> str:
    # Append htmlFragment to the "end of" htmlDocument
    # htmlDocument (e.g. PRX.html):
    #   assumed to be a full document, i.e. <html> <head>...</head> <body>...</body> </html>
    # htmlFragment (e.g. s166.html):
    #   fragment without <html>/<head>/<body>
    # Return "properly formed" HTML document:
    # <html>
    #   <head> ... </head>
    #   <body>
    #     htmlDocument
    #     htmlFragment
    #   </body>
    # </html>
    m = re.match(r"(.*)(</(body|html)>\s*)", htmlFragment, (re.DOTALL|re.IGNORECASE))
    if m:
        raise ValueError("appendHtmlFragmentToHtmlDocument(): Bad htmlFragment")
    m = re.match(r"(.*)(</body>\s*</html>\s*)", htmlDocument, (re.DOTALL|re.IGNORECASE))
    if not m:
        raise ValueError("appendHtmlFragmentToHtmlDocument(): Bad htmlDocument")
    htmlDocument = m.group(1) + htmlFragment + m.group(2)
    return htmlDocument


def htmlEntitize(text: str) -> str:
    # Entitize a plain text string to an HTML string
    html = text \
        .replace("&", "&amp;")\
        .replace('"', "&quot;")\
        .replace("'", "&apos;")\
        .replace("<", "&lt;")\
        .replace(">", "&gt;")\
        .replace("£", "&pound;")
    return html


def htmlSpecialMarkDown(html: str) -> str:
    # Replace our "special markdown" sequences
    # Used for "Clause"s whose text is taken from various database table columns
    # to allow users a very simple way of getting a couple of formatting effects

    # **bold text**
    html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)

    # //italic text//
    html = re.sub(r'//(.+?)//', r'<i>\1</i>', html)

    # __underlined text__
    html = re.sub(r'__(.+?)__', r'<u>\1</u>', html)

    return html


def previewHeaderHtml():
    return "<div style=\"z-index:-1; position:absolute; font-size:1200%; opacity:0.5;\">" \
           "    PREVIEW" \
           "</div>"


# Merge variables which may occur in the html
class PayRequestMergeVariables:
    # htmlfunctions.py
    RentTable = "%RentTable%"
    ArrearsTable = "%ArrearsTable%"
    ChargesTable = "%ChargesTable%"
    HeaderOverlay = "%HeaderOverlay%"


def mergeChargesTable(htmlText, charges):
    # htmlfunctions.py
    chargeHtml = ""
    if charges:
        for charge in charges:
            chargeHtml += createHtmlTableRow(charge[0], charge[1])
    return htmlText.replace(PayRequestMergeVariables.ChargesTable, chargeHtml)


# Creates a single html table row with two cells, the right of which is aligned right (since it's the numerical value)
def createHtmlTableRow(leftCell, rightCell):
    # htmlfunctions.py
    return "<tr>" \
           "    <td>{}</td>" \
           "    <td align=\"right\">{}</td>" \
           "</tr>" \
        .format(htmlEntitize(leftCell), htmlEntitize(rightCell))


def constructCharges(chargesList):
    # mailvariables.py
    charges = []

    for charge in chargesList:
        chargeDetail = "{}{}:".format(charge["ChargeDetails"],
                                      " - balance owing" if charge["ChargeBalance"] < charge["ChargeTotal"] else "")
        chargeAmount = moneyToStr(charge["ChargeBalance"], commas=False, pound=True)

        charges.append([chargeDetail, chargeAmount])

    return charges


def formatCharges(mergeDict):
    # htmlfunctions.py, eprpayrequestfunctions.py
    mergeDict["ChargeDetails"] = "\n".join([charge[0] for charge in mergeDict["Charges"]])
    mergeDict["ChargeAmounts"] = "\n".join([charge[1] for charge in mergeDict["Charges"]])


UkDateFormat = "%d-%b-%Y"
UkDateFormatYear2 = "%d-%b-%y"
