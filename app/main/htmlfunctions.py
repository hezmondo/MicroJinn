import pathlib
import re
import os
import typing
from app.main.exceptions import HtmlParseException
from app.main.mergingfunctions import createHtmlTableRow, mergeChargesTable, PayRequestMergeVariables


# LL: htmlfunctions.py should hold all functions that relate to the alteration of html text
# Here we merge templates and produce htmltext


# This class is used to merge a html template and repeatedly merge variables into it producing a html output
# LL: This should prevent the Python having to repeatedly read the same template for repeated production of the
# same mail item
class BuildHtmlTemplate:
    def __init__(self, mergeFile: str):
        # Open the html file and read the html as a string
        self.htmlTemplateText = readHtmlTemplateFileWithExpandCss(mergeFile)

    def getVariableMergedHtml(self, mergeDict, mailingType, previewOnly):
        # Merge variables provided by mergeDict into the template text
        htmlText = self.htmlTemplateText
        # Evaluate and replace any <!-- %if conditionals etc.
        htmlText = mergeConditionals(htmlText, mergeDict)

        # Add preview marks if this is a preview
        # For this to work the variable %HeaderOverlay% must be present in the template file
        headerHtml = previewHeaderHtml() if previewOnly else ""
        htmlText = htmlText.replace(PayRequestMergeVariables.HeaderOverlay, headerHtml)

        # Replace each known clause in the html string with its merge value.
        # e.g. replace all occurrences of %TotalDue% with £123.45
        # Also do any "**this is in bold**" etc. markdown substitutions
        # Also replace any new line characters '\n' with their html equivalent line break '<br />'
        htmlText = doHtmlMergeDictSubstitutions(mergeDict, htmlText)

        # If we have values for the rent statement in the dictionary, build a 2x1 html table row,
        # with RentStat in the left cell and PeriodRentDue in the right cell
        # Default to empty string, as if there are no rent stat variables available,
        # we still want to replace %RentTable%" with empty string i.e. delete the text
        rentTableHtml = ""
        if mailingType == MailingType.Pr and mergeDict["RentStat"] and mergeDict["PeriodRentDue"]:
            rentTableHtml = createHtmlTableRow(mergeDict["RentStat"], mergeDict["PeriodRentDue"])
        htmlText = htmlText.replace(PayRequestMergeVariables.RentTable, rentTableHtml)

        # Similarly for the arrears rows in the table
        arrearsTableHtml = ""
        if mailingType == MailingType.Pr or mailingType == MailingType.Account:
            if mergeDict["ArrearsStat"] and mergeDict["RentArrears"]:
                arrearsTableHtml = createHtmlTableRow(mergeDict["ArrearsStat"], mergeDict["RentArrears"])
            htmlText = htmlText.replace(PayRequestMergeVariables.ArrearsTable, arrearsTableHtml)

            # Similarly for charges - for each charge we have create and add another row to be merged in
        htmlText = mergeChargesTable(htmlText, mergeDict["Charges"])

        return htmlText


def previewHeaderHtml():
    return "<div style=\"z-index:-1; position:absolute; font-size:1200%; opacity:0.5;\">" \
           "    PREVIEW" \
           "</div>"


def doHtmlMergeDictSubstitutions(mergeDict: dict, htmlText: str) -> str:
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
        if search not in htmlText:
            continue
        # the replacement we are going to make
        replace = str(subst[1]) if subst[1] is not None else ""
        # entitize the HTML, i.e. protect special HTML characters like "<" etc.
        # after this the replacement text is legal HTML
        replace = htmlEntitize(replace)
        # deal with our "special markdown" sequences, like "**this is bold**""
        # note that we *only* do this on certain, specific variables
        if variableName in ["Clause1", "Clause2", "Clause3", "Clause4", "Clause5",
                            "ClauseA", "ClauseB",
                            "ArrearsClause"]:
            replace = htmlSpecialMarkDown(replace)
        # the replacements are intended so every newline should be marked as a "<br>" in the resulting HTML
        replace = htmlNewlinesToBreaks(replace)
        # replace all occurrences
        htmlText = htmlText.replace(search, replace)

    return htmlText


def readHtmlTemplateFileWithExpandCss(htmlFile: str) -> str:
    # Read in an HTML (letter/email) "template" file from Paths.MergeDocs()
    # If there are any <link href="letters.css" rel="stylesheet" type="text/css"> lines
    # "expand" them to replace with the actual content of the CSS file
    # This is required because email/docx-from-HTML must have the CSS in-line, not in an external file

    # Read in the HTML template file
    htmlText = readHtmlFromFile(htmlFile)
    # Find any <link href="letters.css" rel="stylesheet" type="text/css"> lines
    # and replace by the CSS file contents
    m = re.search(r'<head\s*>\n?(.*)</head\s*>', htmlText, flags=(re.DOTALL|re.IGNORECASE))
    if m:
        beforeHead = htmlText[:m.start()]
        afterHead = htmlText[m.end():]
        head = m.group(1)
        lines = head.splitlines()
        expandedLines = ""
        for line in lines:
            # search for <link ... rel="stylesheet" ... >
            m = re.search("<link[^>]*rel=['\"]stylesheet['\"][^>]*>", line, flags=re.IGNORECASE)
            if m:
                # search for <link ... href="..." ... >
                m = re.search("<link[^>]*href=['\"]([^'\"]*)['\"][^>]*>", line, flags=re.IGNORECASE)
                if m:
                    href = m.group(1)
                    if href:
                        # locate ".css" file
                        cssFilePath = os.path.join(mergedir, 'letters.css')
                        # insert file content, surrounded by <style>...</style>
                        with open(cssFilePath, "r") as f:
                            line = f.read()
                        if not line.endswith("\n"):
                            line += "\n"
                        line = "<style>\n" + line + "</style>"
            expandedLines += line + "\n"
        # replace original <head> section with new one
        head = "<head>\n" + expandedLines + "</head>"
        htmlText = beforeHead + head + afterHead

    return htmlText


def appendHtmlFragmentToHtmlDocument(htmlDocument: str, htmlFragment: str) -> str:
    # Append htmlFragment to the "end of" htmlDocument
    # htmlDocument (e.g. PR1.html):
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


def mergeHtmlDocuments(htmlInto: str, htmlFroms: typing.List[str], append: bool=True, pageBreak: bool=True,
                       horizontalRule: bool=False) -> str:
    # parse htmlInto into <head> & <body>
    htmlIntoHead, htmlIntoBody = htmlHeadBody(htmlInto)
    for htmlFrom in htmlFroms:
        # parse htmlFrom into <head> & <body>
        htmlFromHead, htmlFromBody = htmlHeadBody(htmlFrom)
        # if htmlFrom has <head> we replace any htmlInto <head> with that
        # this is not "perfect", but we can't merge them
        # so we retain whatever is the <head> of the latest htmlFrom, for right or for wrong
        if htmlFromHead:
            htmlIntoHead = htmlFromHead
        # insert htmlFrom <body> at beginning of existing htmlInto <body>
        intersperser = ''
        # follow it by a horizontal rule (shows up in browser)
        if horizontalRule:
            intersperser += '<hr style="width: 100%;" />\n'
        # and a page-break (shows up in editors)
        if pageBreak:
            intersperser += '<p style="page-break-before: always;"></p>\n'
        # if append, append to end of body, else insert into start of body
        if append:
            htmlIntoBody = htmlIntoBody + intersperser + htmlFromBody
        else:
            htmlIntoBody = htmlFromBody + intersperser + htmlIntoBody

        # tidy up newlines
        if not htmlIntoHead.startswith("\n"):
            htmlIntoHead = "\n" + htmlIntoHead
        if not htmlIntoHead.endswith("\n"):
            htmlIntoHead = htmlIntoHead + "\n"
        if not htmlIntoBody.startswith("\n"):
            htmlIntoBody = "\n" + htmlIntoBody
        if not htmlIntoBody.endswith("\n"):
            htmlIntoBody = htmlIntoBody + "\n"

    # return complete HTML document
    htmlInto = "<!DOCTYPE html>\n<html>\n<head>"\
            + htmlIntoHead\
            + "</head>\n<body>"\
            + htmlIntoBody\
            + "</body>\n</html>\n"
    return htmlInto


def readHtmlFromFile(filename):
    basedir = os.path.abspath(os.path.dirname('mjinn'))
    mergedir = os.path.join(basedir, 'app/templates/mergedocs')
    htmlFilePath = os.path.join(mergedir, filename)
    # with open(htmlFilePath, "r" encoding="utf-8") as f:
    #     htmlText = f.read()
    with htmlFilePath.open('r', encoding="utf-8") as f:
        htmlText = f.read()
    return htmlText


def writeHtmlToFile(filePath: pathlib.Path, htmlText: str):
    # I don't totally get this, but we must be careful here to specify a suitable encoding
    # on Linux this is always "utf-8",
    # but on Windows the "preferred encoding" is "cp1252"
    # however sometimes this fails on certain characters,
    # I *think* after a paste has been done to insert some external document content
    # in which case it will use/try "utf-8" under Windows too
    # encoding = filesystemfunctions.encodingForWriteTextToFile(htmlText)
    #
    # Scrapped: instead we always use encoding="utf-8" for this
    # see readHtmlFromFile() above
    # we cannot be sure either way, but these two functions should at least match
    f = filePath.open('w', encoding="utf-8")
    try:
        f.write(htmlText)
        f.close()
    except:
        f.close()
        filePath.unlink()
        raise


def createEmailArchiveFile(filePath: pathlib.Path):
    # create empty HTML archive document
    writeHtmlToFile(filePath, "<!DOCTYPE html>\n<html>\n<head>\n</head>\n<body>\n</body>\n</html>\n")


def saveHtmlBackToFile(htmlText: str, filePath: pathlib.Path):
    # overwrite existing html file
    # we do not wish to risk losing its existing content if there is any kind of error
    # so have to do it by writing to a new file and then renaming
    tmpFilePath = filePath.with_suffix(".tmp")
    writeHtmlToFile(tmpFilePath, htmlText)
    tmpFilePath.replace(filePath)


# # # # # # # # # # # # # # # # # # #
#
# F.3 HTML functions
#
# # # # # # # # # # # # # # # # # # #


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


def htmlNewlinesToBreaks(html: str) -> str:
    # Replace newlines in an HTML string with line breaks
    html = re.sub(r"(\r?\n)", r"<br />\1", html)
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


def htmlHeadBody(html: str) -> typing.Tuple[str, str]:
    # A very simple HTML parser
    # Given a well-formed HTML document like:
    # <html>
    #   [ <head> ... </head> ]
    #   <body> ... </body>
    # </html>
    # returns just *the contents of* [ <head>, <body> ]

    # find first occurrence of <html> and last occurrence of </html>
    m = re.search(r'<html[^>]*>\n?(.*)</html[^>]*>(?!.*</html[^>]*>)', html, (re.IGNORECASE|re.DOTALL))
    if not m:
        raise ValueError("htmlHeadBody: <html>...</html> not found")
    html = m.group(1)
    # find optional first occurrence of <head>...</head>
    m = re.search(r'<head[^>]*>\n?(.*)</head[^>]*>(.*)', html, (re.IGNORECASE|re.DOTALL))
    if m:
        head = m.group(1)
        html = m.group(2)
    else:
        head = ""
    # find first occurrence of <body> and last occurrence of </body>
    m = re.search(r'<body[^>]*>\n?(.*)</body[^>]*>(?!.*</body[^>]*>)', html, (re.IGNORECASE|re.DOTALL))
    if not m:
        raise ValueError("htmlHeadBody: <body>...</body> not found")
    body = m.group(1)

    return head, body


def mergeHtmlFile(html: str, mergeDict: dict) -> str:
    pass


def mergeConditionals(html: str, mergeDict: dict) -> str:
    # Called "mergeConditionals" for historical reasons
    # Actually preprocesses the HTML for "directives"
    # and returns the HTML with all directives "expanded"/"acted upon"
    # All directives must be on a line of their own, as an HTML comment, like: <!-- %<directive> <argument(s)> -->
    # e.g. <!-- %if %IsLetter% -->
    # 2 kinds of directives are recognised:
    # 1.  <!-- %if %<variable>% [ == "<value>" ] --> ... <!-- %endif [ %<variable>% ] -->
    #   - includes the enclosed HTML iff <variable> equals <value> (or is not empty/false if no = <value>)
    # 2.  <!-- %include "<file>" -->
    #   - includes the content of <file-path>
    # Directives may be nested

    htmlOut = ""

    # the stack of "%if"s we are currently inside
    ifStack = []
    # whether we are currently outputting lines met (i.e. depends on any "%if" we are presently inside)
    currentlyOutputting = True

    # regular expression to match: <!-- %<directive> ... -->
    reDirective = re.compile(r"\s*<!--\s*%(\S+)\s+(.*?)\s*-->.*")
    # regular expression to match "<file>" (for %include)
    reFilename = re.compile(r'\s*"([^"]*)"\s*')
    # regular expression to match "%<variable>% [ == "<value>" ]" (for %if)
    reIfExpression = re.compile(r'\s*%([^%]+)%(\s*==\s*"([^"]*)"\s*)?\s*')

    # split the HTML into separate lines
    lines = html.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1

        m = reDirective.match(line)

        if not m:
            # not a directive line, just output or skip
            if currentlyOutputting:
                htmlOut += line + "\n"
            continue

        directive = m.group(1).lower()
        arguments = m.group(2)

        if directive == "include":
            # if not currently outputting, just ignore
            if not currentlyOutputting:
                continue

            m2 = reFilename.match(arguments)
            if not m2:
                raise HtmlParseException('<!-- %include must be followed by "<file>"')
            filename = m2.group(1)
            # Read in the included template file
            included = readHtmlFromFile(filename)
            # and recursively call mergeConditionals()
            included = mergeConditionals(included, mergeDict)
            htmlOut += included

        elif directive == "if":
            # if not currently outputting, just push False to the if stack
            if not currentlyOutputting:
                ifStack.append(False)
                continue

            m2 = reIfExpression.match(arguments)
            if not m2:
                raise HtmlParseException('<!-- %if must be followed by %variable%, optionally followed by == "<value>"')
            variable = m2.group(1)
            value = m2.group(3)
            dictValue = mergeDict.get(variable, "")
            # LL: I have added this to prevent IsEmail/IsLetter False prompting incorrect includes
            # This may be an error and those values may need to be sorted
            if dictValue is None or dictValue is False:
                dictValue = ""
            if value is not None:
                # if there is a value, compare string of value to string of dict value (case-insensitive)
                currentlyOutputting = str(value).lower() == str(dictValue).lower()
            else:
                # if there is no value, just see whether dict value exists and is not empty
                currentlyOutputting = dictValue != ""
            # push whether currently outputting to if stack
            ifStack.append(currentlyOutputting)

        elif directive == "endif":
            # pop if stack
            if len(ifStack) == 0:
                raise HtmlParseException('<!-- %endif not matched with a previous <!-- %if')
            ifStack.pop()
            # set currently outputting to previous if stack state
            currentlyOutputting = len(ifStack) == 0 or ifStack[-1]

        else:
            # for anything else, just output or skip
            if currentlyOutputting:
                htmlOut += line + "\n"

    if len(ifStack) != 0:
        raise HtmlParseException('<!-- %if not closed by <!-- %endif at end-of-file')

    return htmlOut


