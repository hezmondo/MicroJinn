from app.main.common import readFromFile
from app.main.functions import moneyToStr, dateToStr, htmlEntitize
from app.main.get import getmaildata, getrentobj_main
from app.main.htmlfunctions import htmlSpecialMarkDown, htmlNewlinesToBreaks

def writeMail(rent_id, income_id, letter_id):
    # This function takes in rent details and outputs a mail item (letter/email)

    rentobj, properties, totcharges = getrentobj_main(rent_id)
    incomedata, allocdata, letterdata, addressdata = getmaildata(rent_id, income_id, letter_id)

    word_variables = {'#advarr#': rentobj.advarrdet if rentobj else "in eleven",
        '#rentpa#': moneyToStr(rentobj.rentpa if rentobj else 11.00, pound=True),
        '#arrears#': moneyToStr(rentobj.arrears if rentobj else 111.00, pound=True),
        '#lastrentdate#': dateToStr(rentobj.lastrentdate) if rentobj else "11/11/2011",
        '#nextrentdate#': dateToStr(rentobj.nextrentdate) if rentobj else "11/11/2011",
        '#paidtodate#': dateToStr(rentobj.paidtodate) if rentobj else "11/11/2011",
        '#rent_type#': "rent charge" if rentobj.tenuredet == "rent charge" else "ground rent",
        '#paytypedet#': incomedata.paytypedet if incomedata else "somepaytype",
        '#payamount#': moneyToStr(incomedata.payamount if incomedata else 111.00, pound=True),
        '#paydate#': dateToStr(incomedata.paydate) if incomedata else "11/11/2011",
        '#payer#': incomedata.payer if incomedata else "some payer",
        '#propaddr#': addressdata.propaddr if addressdata else "some property"
                      }

    subject = letterdata.subject
    part1 = letterdata.part1 if letterdata.part1 else ""
    part2 = letterdata.part2 if letterdata.part2 else ""
    part3 = letterdata.part3 if letterdata.part3 else ""

    subject = doReplace(word_variables, subject)
    part1 = doReplace(word_variables, part1)
    part2 = doReplace(word_variables, part2)
    part3 = doReplace(word_variables, part3)

    mailaddr = addressdata.mailaddr
    mailaddr = mailaddr.split(", ")

    return subject, part1, part2, part3, rentobj, letterdata, addressdata, mailaddr


def doReplace(dict, clause):
    for key, value in dict.items():
        clause = clause.replace(key, value)

    return clause


def doSubstitutions(mergeDict: dict, clause: str) -> str:
    # Given a mergeDict (elements like 'Landlord' -> 'Mr F. Bloggs')
    # Replace each known clause in the html string with its merge value.
    # e.g. replace all occurrences of %TotalDue% with £123.45
    # Also do any "**this is in bold**" etc. markdown substituions
    # Also replace any new line characters '\n' with their html equivalent line break '<br />'
    # do whatever substitions to produce final, safe HTML

    # iterate all items in the dictionary, searching & replacing in the text as we go
    for subst in mergeDict.items():
        # the name of the "variable" in the dictionary
        variableName = subst[0]
        # the sequence we are going to search for in the text
        search = "%" + variableName + "%"
        # optimization: don't do any more here if the search string is not going to be found in the text
        if search not in clause:
            continue
        # the replacement we are going to make
        replace = str(subst[1]) if subst[1] is not None else ""
        # entitize the HTML, i.e. protect special HTML characters like "<" etc.
        # after this the replacement text is legal HTML
        # replace = htmlEntitize(replace)
        # deal with our "special markdown" sequences, like "**this is bold**""
        # note that we *only* do this on certain, specific variables
        # if variableName in ["subject", "part1", "part2", "part3"]:
        #     replace = htmlSpecialMarkDown(replace)
        # the replacements are intended so every newline should be marked as a "<br>" in the resulting HTML
        # replace all occurrences
        clause = clause.replace(variableName, replace)

    return clause
