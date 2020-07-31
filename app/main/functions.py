import typing
import datetime
import decimal
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_DOWN, ROUND_UP
import re
from app.main.exceptions import RentIntegerException

# List of basic functions that don't rely on GUI elements or on specific objects like rents or cases.
# includes string/date/decimal conversion functions

#     """n old periods enables the variables to look backwards e.g. 0 = next rent date, 1 = last rent date,
#        2 = rent date before last, etc.
#
#        If no rent then just pass a list of tuples of variables with associated example
#
#        Might be nice to do it without DbHandler but not sure how receipts could be handled"""
#     # jon: Removed dbHandler=None parameter, not used
#
#     today = datetime.date.today()
#
#     rent_date = annual_rent = period_rent = charges = arrears = tot = period_start_date = period_end_date = \
#         tot_rent_start_date = iswas = s_lastIncomeDate = m_lastIncomeTotal = None
#
#     if rent:
#         if n_periods == 1:
#             rent_date = rent.info['NextRentDate']
#         elif n_periods < 1:
#             rent_date = rent.info['LastRentDate']
#         else:
#             raise Exception("Rent {} tried to call word_variables for a rent date before lastRentDate".format(
#                 rent.info['RentCode']))
#
#         annual_rent = rent.info['Rent']
#         period_rent = rent.periodRent()
#         charges = rent.info['ChargesBalance'] if rent.info['ChargesBalance'] is not None else money(0.00)
#
#         if pay_request and n_periods == 1:
#             arrears = rent.info['Arrears']
#             tot = arrears + charges + period_rent
#         elif pay_request:
#             arrears = rent.info['Arrears'] - period_rent if rent.info['Arrears'] >= period_rent else 0
#             tot = arrears + charges + period_rent
#         else:
#             arrears = rent.info['Arrears']
#             tot = arrears + charges
#
#         period_start_date, period_end_date = rent.payReqDates(rent_date)
#
#         if n_periods < 1:
#             tot_rent_start_date = rent.arrearsStartDate() if arrears > 0 else period_start_date
#         else:
#             tot_rent_start_date = rent.arrearsStartDate()
#
#         iswas = "is" if rent_date > today else "was"
#
#         if rent.dict_lastRec is not None:
#             s_lastIncomeDate = dateToStr(rent.dict_lastRec['PayDate'])
#             m_lastIncomeTotal = money(rent.dict_lastRec['IncomeTotal'])
#         else:
#             s_lastIncomeDate = ""
#             m_lastIncomeTotal = money(0.00)
#
#     word_variables = [
#         ('#AdvArr#', rent.advArr() if rent else "in advance"),
#         ('#AnnualRent#', moneyToStr(annual_rent if rent else 25.00, pound=True)),
#         ('#Arrears#', moneyToStr(arrears if rent else 75.00, pound=True)),
#         ('#BankName#', rent.landlord['BankName'] if rent else "Natwest RH"),
#         ('#BankSortCode#', rent.landlord['BankSortCode'] if rent else "00-00-00"),
#         ('#BankAccountNumber#', rent.landlord['BankAccountNumber'] if rent else "10101010"),
#         ('#BankAccountName#', rent.landlord['BankAccountName'] if rent else "R Hesmondhalgh & D Maloney"),
#         ('#ChargeType#', rent.chargeType() if rent else "ground rent"),
#         ('#ChargeTypeCap#', rent.chargeType().capitalize() if rent else "Ground rent"),
#         ('#ChargesStat#', rent.chargesStatement() if rent else ""),
#         ('#IsWas#', iswas if rent else "'is' or 'was'"),
#         ('#HashCode#', rent.hashCode() if rent else "Abracadabra"),
#         ('#Landlord#', rent.landlord['Name'] if rent else "Richard Hesmondhalgh"),
#         ('#LandlordAddress#', rent.landlord['Address'] if rent else "Hawthorn Dene, School Lane, West Hill, Ottery St. Mary, Devon EX11 1UP"),
#         ('#PaidToDate#', dateToStr(rent.info['PaidToDate']) if rent else "27/09/2008"),
#         ('#LastIncomeDate#', s_lastIncomeDate if rent else "22/02/2002"),
#         ('#LastIncomeTotal#', moneyToStr(m_lastIncomeTotal if rent else 5.00, pound=True)),
#         ('#LastRentDate#', dateToStr(rent.info['LastRentDate']) if rent else "01/06/2014"),
#         ('#Lessor#', rent.lessor() if rent else "Lessor/Rent Charge owner"),
#         ('#MailAddrFlat#', rent.mailAddr().replace("\n", ", ") if rent else ""),
#         ('#Manager#', rent.landlord['Manager'] if rent else "Secure Equity Assets Management Ltd."),
#         ('#ManagerAddress#', rent.landlord['ManagerAddress'] if rent else "Hawthorn Dene, School Lane, West Hill, Ottery St. Mary, Devon EX11 1UP"),
#         ('#ManagerDet#', rent.landlord['ManagerDetails'] if rent else "Registered in England company number 6397879"),
#         ('#NFee#', moneyToStr(rent.info['NFeeTotal'] if rent else 15.00, pound=True)),
#         ('#NextRentDate#', dateToStr(rent.info['NextRentDate']) if rent else "21/01/2012"),
#         ('#NextRentStat#', rent.nextRentStatement() if rent else ""),
#         ('#OwingStat#', rent.newOwingStatement() if rent else ""),
#         ('#Period#', rent.wordPeriodShort() if rent else "half-year or quarter-year e.g.\n'due #Period#ly' = 'due half-yearly'\n'one #Period#'s rent' = 'one half-year's rent'"),
#         ('#PeriodRent#', moneyToStr(period_rent if rent else 12.50, pound=True)),
#         ('#PeriodRentDouble#', moneyToStr(2 * period_rent if rent else 12.50, pound=True)),
#         # ('#PriceBase#', moneyToStr(rent.info['PriceBase'] if rent else 999999.99, pound=True)),
#         ('#Price#', moneyToStr(rent.priceFull() if rent else 999999.99, pound=True)),
#         ('#PricePM#', moneyToStr(rent.pricePM() if rent else 999999.99, pound=True)),
#         ('#PropAddr#', rent.propAddr() if rent else ""),
#         ('#PropAddrFlat#', rent.propAddr().replace("\n", ", ") if rent else ""),
#         ('#ReceiptStat#', "PLACEHOLDER" if rent else "charge details on separate lines"),
#         # THis statement can only be generated
#         # with a specific receipt ID passed, therefore is found at 'run-time' rather than always being accessible
#         ('#RedRent#', rent.reducedRent(False) if rent else 'numerical reduced rent'),
#         ('#RedRentStat#', rent.redRenStatement() if rent else "one sentence statement describing reduced rent"),
#         ('#RentCode#', rent.info['RentCode'] if rent else "DUMMY"),
#         ('#RentOwingPeriod#', "{} to {}".format(dateToStr(rent.arrearsStartDate()) if rent else "01/01/2012",
#                                                 dateToStr(rent.arrearsEndDate()) if rent else "31/12/2012")),
#         ('#RentOwingPeriodStart#', dateToStr(rent.arrearsStartDate()) if rent else "01/01/2012"),
#         ('#RentOwingPeriodEnd#', dateToStr(rent.arrearsEndDate()) if rent else "01/01/2014"),
#         ('#PayRequestRentPeriod#', "{} to {}".format(dateToStr(tot_rent_start_date) if rent else "01/01/2012",
#                                                      dateToStr(period_end_date) if rent else "01/06/2013")),
#         ('#Source#', rent.info['Source'] if rent else "Source"),
#         ('#TenantName#', rent.info['TenantName'] if rent else "Joe Smith"),
#         ('#TenureType#', rent.tenure() if rent else "leasehold"),
#         ('#Today#', dateToStr(today) if rent else dateToStr(today)),
#         ('#TotCharges#', moneyToStr(rent.info['ChargesBalance'] if rent else 999.99, pound=True)),
#         ('#TotalDue#', moneyToStr(tot if rent else 80.00, pound=True)),
#     ]
#
#     # Currently handling receipt statement differently because I didn't want to pass word variables a DbHandler,
#     # but this might be changed, especially when considering letters without a rent
#
#     return {x: y for x, y in word_variables}

# Date, rent, numerical functions

def validateDate(date: str):
    return parseDateSoft(date) is not None


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


def rentInt(num, den, redRent=None):
    # jon: we don't understand exactly what this doing why
    # just leave it as-is
    # laurence: This code takes in "num",the amount money in an income posting that is contributed to the rent payment
    # after costs. "den", is the self.rent.periodRent value.
    # This code attempts to take the num value(rent contribution) and determine how many times it covers the periodRent.
    # Essentially it tries to work out how many periods of rent can be covered by the rent contribution
    # Now if it fails to get an integer value it will try for a reduced rent value before raising an exception

    dec_answer = (num / den).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    dec_answer_rounded = int(dec_answer.quantize(1, rounding=ROUND_HALF_DOWN))

    if abs(dec_answer - dec_answer_rounded) < 0.02:
        return dec_answer_rounded

    elif redRent > 0:
        # Remove a gale of reduced rent if a reducedRent value is present
        rentContribution = num - redRent
        dec_answer = (rentContribution / den).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        dec_answer_rounded = int(dec_answer.quantize(1, rounding=ROUND_HALF_DOWN))
        if abs(dec_answer - dec_answer_rounded) < 0.02:
            # Add one integer value for the reduced rent deducted
            return dec_answer_rounded + 1
    else:
        raise RentIntegerException("bad income multiple of rent")
        # return dec_answer


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


def dateToStr(date):
    # convert a datetime.date to a string in UK format
    # date of `None` returns an empty string
    if date is None:
        return ""
    return date.strftime(UkDateFormat)


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


def parseDateHard(date: str, parent=None) -> typing.Union[datetime.date, None]:
    # converts a str (D/M/Y) to a datetime.date
    # with an ErrorMsgBox() if str not a valid date
    # None => str not a valid date
    pyDate = parseDateSoft(date)
    # if pyDate is None:
    #     from widgets.messageboxes import ErrorMsgBox
    #     ErrorMsgBox("Date '{}' not in correct format.\nLooking for D/M/Y".format(date), parent).exec()
    #     return None
    return pyDate


def parseDateSoft(date: str) -> typing.Union[datetime.date, None]:
    # converts a str (D/M/Y) to a datetime.date
    # None => str not a valid date
    try:
        return datetime.datetime.strptime(date, UkDateFormat).date()
    except ValueError:
        try:
            return datetime.datetime.strptime(date, UkDateFormatYear2).date()
        except ValueError:
            return None


def isValidFullDateStr(date: str) -> bool:
    return re.fullmatch(r"\d\d?/\d\d?/\d\d\d\d", date) is not None


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




UkDateFormat = "%d/%m/%Y"
UkDateFormatYear2 = "%d/%m/%y"
