from common.functions import htmlEntitize, moneyToStr


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


