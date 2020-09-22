#!/usr/bin/env python3
from sys import argv, exit
import os
import argparse
import re

# Default options
COL = 0
STDIN = ""  # made to hold standard input for multiple functions

# get column length
try:
    COL = int(os.get_terminal_size()[0])
except:
    try:
        COL = int(os.get_terminal_size(0)[0])
    except:
        COL = int(os.get_terminal_size(1)[0])

terms = []  # global array that contains all search terms


# RC info

progname = os.path.basename(argv[0])
VERSION = "v1.5"  # Program version
files_array = []  # Array options with file names
name_array = []  # Array options with database names
path_array = []  # Array options with paths to database files
git_array = []  # Array options with the git repo to update the databases


def scrapeRC():
    """ This function runs on init to get settings for all the databases used for searching
    """
    divider = []

    paths = [
        "/etc/.searchsploit_rc",
        os.path.expanduser("~/.searchsploit_rc"),
        os.path.expanduser("~/.local/.searchsploit_rc"),
        os.path.abspath(os.path.join(os.sys.path[0], ".searchsploit_rc"))
    ]

    for p in paths:
        if os.path.exists(p):
            with open(p, "r") as settingsFile:
                settings = settingsFile.read().split("\n")
                settingsFile.close()
                break
    else:
        print("ERROR: Cannot find .searchsploit_rc\nPlease make sure it is located in one of its well known locations.")
        print("It can be anywhere in one of these locations:")
        for p in paths:
            print("\"{0}\"".format(p))
        exit(2)

    for i in settings:
        if(i == "" or i[0] == "#"):
            continue  # Ignores lines that are empty or are just comments
        divider = i[:len(i)-2].split("+=(\"")
        if divider[0] == "files_array":
            files_array.append(divider[1])
        elif divider[0] == "name_array":
            name_array.append(divider[1])
        elif divider[0] == "path_array":
            path_array.append(divider[1])
        elif divider[0] == "git_array":
            git_array.append(divider[1])

    # This section is to remove database paths that do not exist
    larray = len(files_array)
    for i in range(larray - 1, -1, -1):
        if not os.path.exists(os.path.abspath(os.path.join(path_array[i], files_array[i]))):
            files_array.pop(i)
            name_array.pop(i)
            path_array.pop(i)
            git_array.pop(i)


scrapeRC()

################
## Arg Parser ##
################
parseArgs = None  # Variable to hold values from parser
parser = argparse.ArgumentParser(
    prefix_chars="-+/", formatter_class=argparse.RawTextHelpFormatter, prog=os.path.basename(argv[0]))

parser.description = """
==========
 Examples
==========
  %(prog)s afd windows local
  %(prog)s -t oracle windows
  %(prog)s -p 39446
  %(prog)s linux kernel 3.2 --exclude="(PoC)|/dos/"
  %(prog)s linux reverse password

  For more examples, see the manual: https://www.exploit-db.com/searchsploit

=========
 Options
=========   
"""
parser.epilog = """
=======
 Notes
=======
 * You can use any number of search terms.
 * Search terms are not case-sensitive (by default), and ordering is irrelevant.
   * Use '-c' if you wish to reduce results by case-sensitive searching.
   * And/Or '-e' if you wish to filter results by using an exact match.
 * Use '-t' to exclude the file's path to filter the search results.
   * Remove false positives (especially when searching using numbers - i.e. versions).
 * When updating or displaying help, search terms will be ignored.
"""

# Arguments
parser.add_argument("searchTerms", nargs="*")

searchHeader = parser.add_argument_group(
    "Search Terms", "These arguments are used to manipulate the results of a search to get more specific searches.")
searchHeader.add_argument("-c", "--case", action="store_true",
                          help="Perform a case-sensitive search (Default is inSEnsITiVe).")
searchHeader.add_argument("-e", "--exact", action="store_true",
                          help="Perform an EXACT match on exploit title (Default is AND) [Implies \"-t\"].")
searchHeader.add_argument("-i", "--ignore", action="store_true",
                          help="Adds any redundant term in despite it possibly giving false positives.")
searchHeader.add_argument("-s", "--strict", action="store_true",
                          help="Perform a strict search, so input values must exist, disabling fuzzy search for version range e.g. \"1.1\" would not be detected in \"1.0 < 1.3\"")
searchHeader.add_argument("-t", "--title", action="store_true",
                          help="Search JUST the exploit title (Default is title AND the file's path).")
searchHeader.add_argument("--exclude", nargs="*", type=str, default=list(), metavar="[terms]",
                          help="Remove certain terms from the results. Option best added after all other terms have been gathered.")

outputHeader = parser.add_argument_group(
    "Output", "These arguments drastically change the output given by the program. This can vary from how the results are listed to giving information on one specific exploit.")
outputHeader.add_argument("-j", "--json", action="store_true",
                          help="Show result in JSON format.")
outputHeader.add_argument("-o", "--overflow", action="store_true",
                          help="Exploit titles are allowed to overflow their columns.")
# TODO: Add verbose
outputHeader.add_argument("-w", "--www", action="store_true",
                          help="Show URLs to Exploit-DB.com rather than the local path.")
outputHeader.add_argument("--id", action="store_true",
                          help="Display the EDB-ID value rather than local path.")

outputHeader.add_argument("--colour", action="store_false",
                          help="Disable colour highlighting in search results.")

commandsHeader = parser.add_argument_group(
    "EDB Tools", "These commands involve functions on individual EDB's.")
parserCommands = commandsHeader.add_mutually_exclusive_group()
parserCommands.add_help = True
parserCommands.add_argument("-m", "--mirror", type=int, default=None,
                            metavar="[EDB-ID]", help="Mirror (aka copies) an exploit to the current working directory.")
parserCommands.add_argument("-x", "--examine", type=int, default=None,
                            metavar="[EDB-ID]", help="Examine (aka opens) the exploit using \$PAGER.")
parserCommands.add_argument("-p", "--path", type=int, default=None,
                            metavar="[EDB-ID]", help="Show the full path to an exploit (and also copies the path to the clipboard if possible).")
parserCommands.add_argument("-u", "--update", action="store_true",
                            help="Check for and install any exploitdb package updates (deb or git).")
parserCommands.add_argument("--version", action="version",
                            version="%(prog)s {0}".format(VERSION))

automationHeader = parser.add_argument_group(
    "Automation", "This involves all tools that involve plugins from other tools, such as nmap.")
automationHeader.add_argument("--nmap", metavar="file.xml", nargs="?", type=argparse.FileType("r"), default=None, const=os.sys.stdin,
                              help="Checks all results in Nmap's XML output with service version (e.g.: nmap -sV -oX file.xml).\nUse \"-v\" (verbose) to try even more combinations")

# Argument variable
parseArgs = parser.parse_args()

# Update database check


def update():
    """ This function is used to update all the databases via github (because github is the best update system for databases this size)
    """
    cwd = os.getcwd()
    for i in range(len(files_array)):
        print("[i] Path: " + path_array[i])
        print("[i] Git Pulling: " + name_array[i] + " ~ " + path_array[i])

        # update via git
        os.chdir(path_array[i])  # set path to repos directory
        os.system("git pull -v origin master")
        print("[i] Git Pull Complete")
    os.chdir(cwd)
    return


######################
##  DISPLAY TOOLS   ##
######################
def drawline():
    """ Draws a line in the terminal.
    """
    line = "" * (int(COL) - 1)
    print(line)


def drawline(lim):
    """ Draws a line in the terminal.\n
    @lim: column where the border is suppossed to be
    """
    line = "-" * lim
    line += "+"
    line += "-" * (COL - lim - 2)  # -2 for terminal padding
    print(line)


def highlightTerm(line: str, term)->str:
    """ Part one of new highlighting process. Highlights by adding :8 and :9 as escape characters as ansi takes several lines. the rest is compiled in separater unless autocomp is true\n
    @line: the phrase to be checked\n
    @term: the term that will be found in line and used to highlight the line\n
    @autoComp: [optional] if true, then it will output the string with the flags already turned into ANSI
    """
    # immediate override if colour option is used
    if not parseArgs.colour:
        return line

    # Adjustments for if term is version tuple
    if type(term) is tuple:
        term = term[1] # TODO: Make way to highlight line if fits version parameters

    marker = 0  # marks where the term is first found
    term = term.lower()

    while (line.lower().find(term, marker) >= 0):
        marker = line.lower().find(term, marker)  # update location of new found term
        part1 = line[:marker]
        part2 = line[marker: marker + len(term)]
        part3 = line[marker + len(term):]
        line = "{0}\033[91m{1}\033[0m{2}".format(part1, part2, part3)
        marker += len(term) + 4
    return line


def separater(lim, line1: str, line2: str):
    """ Splits the two texts to fit perfectly within the terminal width
    """
    lim = int(lim)
    if parseArgs.overflow:
        line = line1 + " | " + line2
        print(line)
        return

    line1_length = lim - 1  # subtract 1 for padding
    # -2 for divider padding and -1 for terminal padding
    line2_length = int(COL) - lim - 2 - 1
    format_string = "{{title:{title_length}.{title_length}s}}\033[0m | {{path:{path_length}.{path_length}s}}\033[0m"

    # Escape options for colour
    if not parseArgs.colour:
        print("{{0:{0}.{0}s}} | {{1:{1}.{1}s}}".format(
            line1_length, line2_length).format(line1, line2))
        return

    # increase lim by markers to not include highlights in series
    last_mark = 0
    while (line1.find("\033[91m", last_mark, line1_length + 5) >= 0):
        line1_length += 5
        last_mark = line1.find("\033[91m", last_mark, line1_length + 5) + 5
    last_mark = 0
    while (line1.find("\033[0m", last_mark, line1_length + 4) >= 0):
        line1_length += 4
        last_mark = line1.find("\033[0m", last_mark, line1_length + 4) + 4
    last_mark = 0
    while (line2.find("\033[91m", last_mark, line2_length + 5) >= 0):
        line2_length += 5
        last_mark = line2.find("\033[91m", last_mark, line2_length + 5) + 5
    last_mark = 0
    while (line2.find("\033[0m", last_mark, line2_length + 4) >= 0):
        line2_length += 4
        last_mark = line2.find("\033[0m", last_mark, line2_length + 4) + 4

    # Creating format string for print
    fstring = format_string.format(
        title_length=line1_length, path_length=line2_length)
    line = fstring.format(title=line1, path=line2)
    print(line)


##############################
##  DATABASE MANIPULATION   ##
##############################
def cpFromDb(path, id):
    """ Returns database array of search for given id.\n
    path: absolute path of database\n
    id: the EDBID that is searched for in database
    """
    dbFile = open(path, "r", encoding="utf8")
    db = dbFile.read().split('\n')
    for lines in db:
        if lines.split(",")[0] == str(id):
            dbFile.close()
            return lines.split(",")
    dbFile.close()
    return []


def findExploit(id):
    """ This Function uses cpFromDB to iterate through all known databases and return exploit and the database it was found in\n
    @id: EDBID used to search all known databases\n
    @return: exploit[], database path
    """
    exploit = []
    for i in range(len(files_array)):
        exploit = cpFromDb(os.path.abspath(
            os.path.join(path_array[i], files_array[i])), id)
        if exploit == []:
            continue
        else:
            return i, exploit

baseVersion = re.compile(r'((?:(?:<)\s*)|(?:[RrVv]))?((?:\d+(?:\.(?:\d+|x))+)|(?:\d+))')

def hasVersion(term: str)->bool:
    """ Returns true if the string contains any numbers that could resemble a verison
    """
    return (len(baseVersion.findall(term)) > 0)

def getVersion(term: str):
    return baseVersion.findall(term) # returns the first found object, taking tuple out of list

def cmpVersion(leftVersion: str, rightVersion: str)->int:
    """ Compares the two versions and returns an integer depending on which one if newer
    """
    leftComponent = leftVersion.split(".")
    rightComponent = rightVersion.split(".")
    for i in range(min(len(leftComponent), len(rightComponent))):
        if (leftComponent[i] != rightComponent[i]):
            # Dealing with wildcard scenarios
            if ("x" in leftComponent[i]):
                if (len(re.findall("((?:{0})|(?:{1}))$".format(leftComponent[i],leftComponent[i].replace("x","\\d*")), rightComponent[i])) > 0):
                    # if the string matches itself or regex replacing all x's with \d's, then it is a match
                    return 0
            elif ("x" in rightComponent[i]):
                if (len(re.findall("((?:{0})|(?:{1}))$".format(rightComponent[i],rightComponent[i].replace("x","\\d*")), leftComponent[i])) > 0):
                    # if the string matches itself or regex replacing all x's with \d's, then it is a match
                    return 0

            # Removing excess chars
            # print(leftComponent[i], rightComponent[i])
            for j in re.findall("([A-Za-z]+)", leftComponent[i]):
                leftComponent[i] = leftComponent[i].replace(j, "")
            for j in re.findall("([A-Za-z]+)", rightComponent[i]):
                rightComponent[i] = rightComponent[i].replace(j, "")
            return int(rightComponent[i]) - int(leftComponent[i])
    return len(rightComponent) - len(leftComponent) # if they are equal up their shortest version, then the latest is the longest version

def validTerm(argsList):
    """ Takes the terms inputed and returns an organized list with no repeats and no poor word choices
    """
    invalidTerms = ["microsoft", "microsoft windows", "apache", "ftp",
                    "http", "linux", "net", "network", "oracle", "ssh", "ms-wbt-server", "unknown", "none"]
    dudTerms = ["unknown", "none"]
    if parseArgs.exact:
        return argsList
    argsList.sort()
    argslen = len(argsList)
    for i in range(argslen - 1, -1, -1):
        if (argsList[i].lower() in dudTerms):
            argsList.pop(i)
        elif (argsList[i].lower() in invalidTerms and not parseArgs.ignore):
            print(
                "[-] Skipping term: " + argsList[i] + "   (Term is too general. Please re-search manually:")
            argsList.pop(i)
            # Issues, return with something
        elif argsList[i].lower() in parseArgs.exclude:
            argsList.pop(i)
        elif not parseArgs.case:
            argsList[i] = argsList[i].lower()
    argsList.sort()
    argslen = len(argsList)
    for i in range(argslen - 1, 0, -1):
        if (argsList[i] == argsList[i-1]):
            argsList.pop(i)
        # what to do if the list ends up empty afterwards
    if (len(argsList) == 0):
        print("Looks like those terms were too generic.")
        print("if you want to search with them anyway, run the command again with the -i arguement")
        exit()

    # Converting certain terms into version terms
    for i in range(len(argsList)):
        if not parseArgs.strict and hasVersion(argsList[i]):
            # Getting first result from list
            argsList[i] = getVersion(argsList[i])[0]

    return argsList


def searchdb(path="", terms=[], cols=[], lim=-1):
    """ Searches for terms in the database given in path and returns the requested columns of positive matches.\n
    @path: the path of the database file to search\n
    @terms: a list of terms where all arguements must be found in a line to flare a positive match\n
    @cols: the columns requested in the order given. ex: cols=[2,0] or title, id\n
    @lim: an integer that counts as the limit of how many search results are requested\n
    @return: database array with positive results
    """
    searchTerms = []
    tmphold = []
    if parseArgs.exact:
        tmpstr = str(terms[0])
        for i in range(1, len(terms)):
            tmpstr += " " + terms[i]
        terms.clear()
        terms.append(tmpstr)
    dbFile = open(path, "r", encoding="utf8")
    db = dbFile.read().split('\n')
    for lines in db:
        if (lines != ""):
            for ex in parseArgs.exclude: # Removing positive lines with excluded values
                if parseArgs.case and ex in lines:
                    break
                elif ex in lines.lower():
                    break
            else:
                for term in terms:
                    if type(term) is str: # separate versions from search terms
                        if parseArgs.title:
                            line = lines.split(",")[2]
                            if parseArgs.case:
                                if term not in line:
                                    break
                            elif term not in line.lower():
                                break
                        elif parseArgs.case:
                            if term not in lines:
                                break
                        elif term not in lines.lower():
                            break
                    elif type(term) is tuple:
                        # skipping if strict
                        if parseArgs.strict:
                            break
                        line = lines.split(",")[2]
                        versions = getVersion(line)
                        versionCompatible = False # helps for the or status here
                        if (len(versions) == 0):
                            break # if no versions could be detected in line, throw out line
                        if (term[0] != "") and "<" not in term[0]: # version has r or s in front
                            for v in versions:
                                if (v[0].lower() != term[0]):
                                    continue # skip this if version doesnt start with same tag
                                versionCompatible = versionCompatible or (cmpVersion(term[1], v[1]) >= 0)
                                # this will only ever be true if just one is true
                            if not versionCompatible:
                                break
                        elif "<" in term[0]:
                            for v in versions:
                                versionCompatible = versionCompatible or (cmpVersion(term[1], v[1]) <= 0)
                            if not versionCompatible:
                                break
                        else:
                            for v in versions:
                                versionCompatible = versionCompatible or (cmpVersion(term[1], v[1]) >= 0)
                            if not versionCompatible:
                                break
                else:
                    for i in cols:
                        space = lines.split(",")
                        tmphold.append(space[i])
                    searchTerms.append(tmphold)
                    tmphold = []
        if(lim != -1 and len(searchTerms) >= lim):
            break
    dbFile.close()
    return searchTerms


def searchsploitout():
    """ Convoluted name for the display. takes the global search terms and prints out a display iterating through every database available and printing out the results of the search.
    """
    # ## Used in searchsploitout/nmap's XML

    # xx validating terms
    validTerm(terms)
    if parseArgs.json:
        jsonDict = {}
        temp = ""
        for i in terms:
            temp += i + " "
        jsonDict["SEARCH"] = temp[:-1]  # Adding the search terms
        searchs = []
        try:
            for i in range(len(files_array)):
                jsonDict["DB_PATH_" + name_array[i].upper()] = path_array[i]
                searchs.clear()
                query = searchdb(os.path.abspath(os.path.join(
                    path_array[i], files_array[i])), terms, [2, 0, 3, 4, 5, 6, 1])
                for lines in query:
                    searchs.append({"Title": lines[0].replace('"', ""), "EDB-ID": int(lines[1]), "Date": lines[2], "Author": lines[3].replace(
                        '"', ""), "Type": lines[4], "Platform": lines[5], "Path": path_array[i] + "/" + lines[6]})
                jsonDict["RESULTS_" + name_array[i].upper()] = searchs.copy()
                searchs.clear()
            import json.encoder
            jsonResult = json.dumps(
                jsonDict, indent=4, separators=(", ", ": "))
            print(jsonResult)
        except KeyboardInterrupt:
            pass
        return

    # xx building terminal look
    # the magic number to decide how much space is between the two subjects
    lim = int((COL - 3)/2)

    # manipulate limit if ID is used
    if parseArgs.id:
        lim = int(COL * 0.8)
    query = []  # temp variable thatll hold all the results
    try:
        for i in range(len(files_array)):
            if parseArgs.id:
                query = searchdb(os.path.abspath(os.path.join(
                    path_array[i], files_array[i])), terms, [2, 0])
            elif parseArgs.www:
                query = searchdb(os.path.abspath(os.path.join(
                    path_array[i], files_array[i])), terms, [2, 1, 0])
            else:
                query = searchdb(os.path.abspath(os.path.join(
                    path_array[i], files_array[i])), terms, [2, 1])

            if len(query) == 0:  # is the search results came up with nothing
                print(name_array[i] + ": No Results")
                continue
            drawline(COL//4)
            separater(COL//4, name_array[i] + " Title", "Path")
            separater(COL//4, "", os.path.abspath(path_array[i]))
            drawline(COL//4)  # display title for every database
            drawline(lim)
            for lines in query:
                # Removing quotes around title if present
                if (lines[0][0] == "\"" or lines[0][0] == "\'"):
                    lines[0] = lines[0][1:]
                if (lines[0][-1] == "\"" or lines[0][-1] == "\'"):
                    lines[0] = lines[0][:-1]

                if parseArgs.www:  # if requesting weblinks. shapes the output for urls
                    lines[1] = "https://www.exploit-db.com/" + \
                        lines[1][:lines[1].index("/")] + "/" + lines[2]

                # substring path with title
                if lines[1].startswith(name_array[i].lower()):
                    lines[1] = lines[1][len(name_array[i]) + 1:]

                if parseArgs.colour:
                    for term in terms:
                        lines[0] = highlightTerm(lines[0], term)
                        lines[1] = highlightTerm(lines[1], term)
                separater(lim, lines[0], lines[1])
            drawline(lim)
    except KeyboardInterrupt:
        drawline(lim)
        return


def nmapxml(file=""):
    """ This function is used for xml manipulation with nmap.\n
    @file: string path to xml file\n
    if no file name is given, then it tries stdin\n
    @return: returns true if it fails
    """
    import xml.etree.ElementTree as ET

    global terms
    global STDIN

    # First check whether file exists or use stdin
    try:
        if (type(file) == str):
            contentFile = open(file, "r")
        else:
            contentFile = file  # if file access, link directly to file pointer
        content = contentFile.read()
        contentFile.close()
    except:
        if(not os.sys.stdin.isatty()):
            content = os.sys.stdin.read()
            if content == "" and STDIN != "":
                content = STDIN
            elif content == "" and STDIN == "":
                return False
        else:
            return False

    # stope if blank or not an xml sheet
    if content == "" or content[:5] != "<?xml":
        STDIN = content
        return False
    # Read XML file

    # ## Feedback to enduser
    if (type(file) == str):
        print("[i] Reading: " + highlightTerm(str(file), str(file)))
    else:
        print("[i] Reading: " + highlightTerm(file.name, file.name))
    tmpaddr = ""
    tmpname = ""
    # ## Read in XMP (IP, name, service, and version)
    root = ET.fromstring(content)

    hostsheet = root.findall("host")
    for host in hostsheet:
        # made these lines to separate searches by machine
        tmpaddr = host.find("address").attrib["addr"]
        tmpaddr = highlightTerm(tmpaddr, tmpaddr)

        if (host.find("hostnames/hostname") != None):
            tmpname = host.find("hostnames/hostname").attrib["name"]
            tmpname = highlightTerm(tmpname, tmpname)
        print("Finding exploits for " + tmpaddr +
              " (" + tmpname + ")")  # print name of machine
        for service in host.findall("ports/port/service"):
            if "name" in service.attrib.keys():
                terms.append(str(service.attrib["name"]))
            if "product" in service.attrib.keys():
                terms.append(str(service.get("product")))
            if "version" in service.attrib.keys():
                terms.append(str(service.get("version")))
            validTerm(terms)
            print("Searching terms:", terms)  # displays terms found by xml
            searchsploitout()  # tests search terms by machine
            terms = []  # emptys search terms for next search

    return True


def nmapgrep(file=""):
    """

    """
    global terms
    global STDIN

    # First check whether file exists or use stdin
    try:
        if (type(file) == str):
            contentFile = open(file, "r")
        else:
            contentFile = file
        content = contentFile.read()
        contentFile.close()
    except:
        if(not os.sys.stdin.isatty()):
            content = os.sys.stdin.read()
            if content == "" and STDIN != "":
                content = STDIN
            elif content == "" and STDIN == "":
                return False
        else:
            return False

    # Check whether its grepable
    if (content.find("Host: ") == -1 or not "-oG" in content.split("\n")[0] or content == ""):
        STDIN = content
        return False

    # making a matrix to contain necessary strings
    nmatrix = content.split("\n")
    for lines in range(len(nmatrix) - 1, -1, -1):
        if (nmatrix[lines].find("Host: ") == -1 or nmatrix[lines].find("Ports: ") == -1):
            nmatrix.pop(lines)
        else:
            nmatrix[lines] = nmatrix[lines].split("\t")[:-1]
            nmatrix[lines][0] = nmatrix[lines][0][6:].split(" ")
            # pull hostname out of parenthesis
            nmatrix[lines][0][1] = nmatrix[lines][0][1][1:-
                                                        1] if (len(nmatrix[lines][0][1]) > 2) else ""
            nmatrix[lines][1] = nmatrix[lines][1][7:].split(", ")
            for j in range(len(nmatrix[lines][1])):
                nmatrix[lines][1][j] = nmatrix[lines][1][j].replace(
                    "/", " ").split()[3:]

    # Outputing results from matrix
    for host in nmatrix:
        tmpaddr = highlightTerm(host[0][0], host[0][0])
        tmpname = highlightTerm(host[0][1], host[0][1])
        print("Finding exploits for " + tmpaddr +
              " (" + tmpname + ")")  # print name of machine
        for service in host[1]:
            terms.extend(service)
            validTerm(terms)
            print("Searching terms:", terms)  # displays terms found by grep
            searchsploitout()  # tests search terms by machine
            terms = []  # emptys search terms for next search
    return True

##########################
##  COMMAND FUNCTIONS   ##
##########################


def path(id):
    """ Function used to run the path arguement
    """
    try:
        file, exploit = findExploit(id)
        print(os.path.abspath(os.path.join(path_array[file], exploit[1])))
    except TypeError:
        print("%s does not exist. Please double check that this is the correct id." % id)


def mirror(id):
    """ Function used to mirror exploits
    """
    try:
        ind, exploit = findExploit(id)
    except TypeError:
        print("%s does not exist. Please double check that this is the correct id." % id)
        return
    absfile = path_array[ind]

    currDir = os.getcwd()
    inp = open(os.path.normpath(os.path.join(absfile, exploit[1])), "rb")
    out = open(os.path.join(currDir, os.path.basename(exploit[1])), "wb")
    out.write(inp.read())
    inp.close()
    out.close()
    return


def examine(id):
    """ Function used to run examine arguement
    """
    try:
        ind, exploit = findExploit(id)
    except TypeError:
        print("%s does not exist. Please double check that this is the correct id." % id)
        return
    if exploit[1].endswith(".pdf"):
        import webbrowser
        webbrowser.open(
            "file:///" + os.path.abspath(os.path.join(path_array[ind], exploit[1])), autoraise=True)
    elif(os.sys.platform == "win32"):
        os.system(
            "notepad " + os.path.relpath(os.path.join(path_array[ind], exploit[1])))
    else:
        os.system(
            "pager " + os.path.relpath(os.path.join(path_array[ind], exploit[1])))
    print("[EDBID]:" + exploit[0])
    print("[Exploit]:" + exploit[2])
    print("[Path]:" + os.path.abspath(os.path.join(path_array[ind], exploit[1])))
    print("[URL]:https://www.exploit-db.com/" +
          exploit[1].split("/")[0] + "/" + exploit[0])
    print("[Date]:" + exploit[3])
    print("[Author]:" + exploit[4])
    print("[Type]:" + exploit[5])
    print("[Platform]:" + exploit[6])
    print("[Port]:" + exploit[7])

##################
##  HOOK SCRIPT ##
##################


def main():
    """ Main function of script. hooks rest of functions
    """

    # Colors for windows
    if parseArgs.colour and os.sys.platform == "win32":
        try:
            import colorama
        except ImportError:
            print(
                "You do not have colorama installed. if you want to run with colors, please run:")
            print(
                "\"pip install colorama\" in your terminal so that windows can use colors.")
            print("Printing output without colors")
            parseArgs.colour = False
        else:
            colorama.init()

    if (len(argv) == 1 and os.sys.stdin.isatty()):
        parser.print_help()  # runs if given no arguements
        return

    # DB Tools
    if parseArgs.mirror != None:
        mirror(parseArgs.mirror)
        return
    elif parseArgs.path != None:
        path(parseArgs.path)
        return
    elif parseArgs.update:
        update()
        return
    elif parseArgs.examine != None:
        examine(parseArgs.examine)
        return

    # formatting exclusions
    if not parseArgs.case:
        for i in range(len(parseArgs.exclude)):
            parseArgs.exclude[i] = parseArgs.exclude[i].lower()

    # Nmap tool
    if parseArgs.nmap != None:
        result = nmapxml(parseArgs.nmap)
        if not result:
            result = nmapgrep(parseArgs.nmap)
            if not result:
                parser.print_help()
                return

    terms.extend(parseArgs.searchTerms)

    if (parseArgs.nmap == None and not os.sys.stdin.isatty()):
        text = str(os.sys.stdin.read())
        terms.extend(text.split())

    searchsploitout()


if __name__ == "__main__":
    main()
