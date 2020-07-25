import pathlib
import re

from common import filesystemfunctions
from common.constants import Paths
from exceptions.exceptions import HtmlParseException


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
            filePath = Paths.MergeDocs() / filename
            filePath = filesystemfunctions.findFileInDataOrCodeDirectory(filePath)
            with filePath.open("r") as f:
                included = f.read()
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

