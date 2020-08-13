#!/usr/bin/env python3
from sys import argv, exit
import os
import argparse

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
files_array = []  # Array options with file names
name_array = []  # Array options with database names
path_array = []  # Array options with paths to database files
git_array = []  # Array options with the git repo to update the databases


def scrapeRC():
    """ This function runs on init to get settings for all the databases used for searching
    """
    divider = []

    try:
        settingsFile = open("/etc/.searchsploit_rc", "r")
    except:
        try:
            settingsFile = open(os.path.expanduser("~/.searchsploit_rc"), "r")
        except:
            settingsFile = open(os.path.abspath(
                os.sys.path[0] + "/.searchsploit_rc"), "r")
            # Checks for config in home directory

    settings = settingsFile.read().split("\n")
    settingsFile.close()

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
    for i in range(larray - 1, 0, -1):
        try:
            tempRead = open(os.path.abspath(os.path.join(path_array[i], files_array[i])),
                            "r", encoding="utf8")
            tempRead.read()
            tempRead.close()
        except:
            try:
                tempRead.close()
            except:
                pass
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
parserCommands = parser.add_mutually_exclusive_group()
# parserSearchTerms = parserCommands.add_argument_group()

# TODO: Build custom formatter to prevent smaller args from having values
parser.add_argument("searchTerms", nargs=argparse.REMAINDER)

parser.add_argument("-c", "--case", action="store_true",
                    help="Perform a case-sensitive search (Default is inSEnsITiVe).")
parser.add_argument("-e", "--exact", action="store_true",
                    help="Perform an EXACT match on exploit title (Default is AND) [Implies \"-t\"].")
parser.add_argument("-i", "--ignore", action="store_true",
                    help="Adds any redundant term in despite it possibly giving false positives.")
parser.add_help = True
parser.add_argument("-j", "--json", action="store_true",
                    help="Show result in JSON format.")
parserCommands.add_argument("-m", "--mirror", type=int, default=None,
                            metavar="[EDB-ID]", help="Mirror (aka copies) an exploit to the current working directory.")
parser.add_argument("-o", "--overflow", action="store_true",
                    help="Exploit titles are allowed to overflow their columns.")
parserCommands.add_argument("-p", "--path", type=int, default=None,
                            metavar="[EDB-ID]", help="Show the full path to an exploit (and also copies the path to the clipboard if possible).")
parser.add_argument("-t", "--title", action="store_true",
                    help="Search JUST the exploit title (Default is title AND the file's path).")
parser.add_argument("-u", "--update", action="store_true",
                    help="Check for and install any exploitdb package updates (deb or git).")
parser.add_argument("-w", "--www", action="store_true",
                    help="Show URLs to Exploit-DB.com rather than the local path.")
parserCommands.add_argument("-x", "--examine", type=int, default=None,
                            metavar=("[EDB-ID]"), help="Examine (aka opens) the exploit using \$PAGER.")
parser.add_argument("--colour", action="store_false",
                    help="Disable colour highlighting in search results.")
parser.add_argument("--id", action="store_true",
                    help="Display the EDB-ID value rather than local path.")
parser.add_argument("--nmap", metavar="file.xml", nargs="?", type=argparse.FileType("r"), default=None, const=os.sys.stdin,
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
        os.system("git pull -v upstream master")
        print("[i] Git Pull Complete")
    os.chdir(cwd)
    return


######################
##  DISPLAY TOOLS   ##
######################
def drawline():
    """ Draws a line in the terminal.
    """
    line = ""
    for i in range(int(COL)):
        line += "-"
    print(line)


def drawline(lim):
    """ Draws a line in the terminal.\n
    @lim: column where the border is suppossed to be
    """
    line = ""
    for i in range(lim):
        line += "-"
    line += "+"
    while len(line) < COL:
        line += "-"
    print(line)


def highlightTerm(line, term, autoComp=False):
    """ Part one of new highlighting process. Highlights by adding :8 and :9 as escape characters as ansi takes several lines. the rest is compiled in separater unless autocomp is true\n
    @line: the phrase to be checked\n
    @term: the term that will be found in line and used to highlight the line\n
    @autoComp: [optional] if true, then it will output the string with the flags already turned into ANSI
    """
    try:
        term = term.lower()
        part1 = line[:line.lower().index(term)]
        part2 = line[line.lower().index(
            term): line.lower().index(term) + len(term)]
        part3 = line[line.lower().index(term) + len(term):]
        line = part1 + ':8' + part2 + ':9' + part3
        if autoComp:
            line = line.replace(":8", '\033[91m').replace(":9", '\033[0m')
    except:
        line = line
    return line


def separater(lim, line1, line2):
    """ Splits the two texts to fit perfectly within the terminal width
    """
    if parseArgs.overflow:
        line = line1 + " | " + line2
        line = line.replace(":8", '\033[91m').replace(":9", '\033[0m')
        print(line)
        return

    # increase lim by markers to not include highlights in series
    if ":8" in line1:
        lim += 2
        if ":9" in line1:
            lim += 2

    if (len(line1) >= lim):
        line1 = line1[:lim-1]
        if line1.count(":8") > line1.count(":9"):
            if line1[len(line1)-1:] == ":8":
                line1 = line1[:len(line1)-2]
            if line1[-1] == ":":
                line1 += "9"
            else:
                line1 += ":9"
        if line1[-1] == ":":
            line1 = line1[:len(line1)-2]
    while len(line1) <= lim:
        line1 += " "
    if(len(line2) >= COL-lim):
        line2 = line2[:lim-1]
        if line2.count(":8") > line2.count(":9"):
            if line2[len(line2)-1:] == ":8":
                line2 = line2[:len(line2)-2]
            elif line2[-1] == ":":
                line2 += "9"
            else:
                line2 += ":9"
        if line2[-1] == ":":
            line2 = line2[:len(line2)-2]

    max = COL
    if ":8" in line1:
        max += 2
    if ":9" in line1:
        max += 2
    if ":8" in line2:
        max += 2
    if ":9" in line2:
        max += 2

    line = line1 + " | " + line2
    if(len(line) > max):
        line = line[:max]
        if line.count(":8") > line.count(":9"):
            if line[len(line)-1:] == ":8":
                line = line[:len(line)-2]
            if line[-1] == ":":
                line += "9"
            else:
                line += ":9"
        if line[-1] == ":":
            line = line[:len(line)-2]

    line = line.replace(":8", '\033[91m').replace(":9", '\033[0m')
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
    for i in range(argslen - 1, 0, -1):
        if (argsList[i].lower() in dudTerms):
            argsList.pop(i)
        elif (argsList[i].lower() in invalidTerms and not parseArgs.ignore):
            print(
                "[-] Skipping term: " + argsList[i] + "   (Term is too general. Please re-search manually:")
            argsList.pop(i)
            # Issues, return with something
        elif not parseArgs.case:
            argsList[i] = argsList[i].lower()
    argsList.sort()
    argslen = len(argsList)
    for i in range(argslen-1, 1, -1):
        if (argsList[i] == argsList[i-1]):
            argsList.pop(i)
        # what to do if the list ends up empty afterwards
    if (len(argsList) == 0):
        print("Looks like those terms were too generic.")
        print("if you want to search with them anyway, run the command again with the -i arguement")
        exit()

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
            for term in terms:
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
            drawline(lim)
            separater(COL/4, name_array[i] + " Title", "Path")
            separater(COL/4, "", os.path.abspath(path_array[i]))
            drawline(lim)  # display title for every database
            for lines in query:
                if parseArgs.www:  # if requesting weblinks. shapes the output for urls
                    lines[1] = "https://www.exploit-db.com/" + \
                        lines[1][:lines[1].index("/")] + "/" + lines[2]
                if parseArgs.colour:
                    for term in terms:
                        lines[0] = highlightTerm(lines[0], term)
                        lines[1] = highlightTerm(lines[1], term)
                if parseArgs.id:
                    # made this change so that ids get less display space
                    separater(int(COL * 0.8), lines[0], lines[1])
                else:
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
    # making sure beautiful soup is importable first
    try:
        from bs4 import BeautifulSoup
    except:
        print(
            "Error: you need to have beautifulsoup installed to properly use this program")
        print("To install beautifulsoup, run 'pip install beautifulsoup4' in your commandline.")
        return False
    # Read XML file

    # ## Feedback to enduser
    if (type(file) == str):
        print("[i] Reading: " + highlightTerm(str(file), str(file), True))
    else:
        print("[i] Reading: " + highlightTerm(file.name, file.name, True))
    tmpaddr = ""
    tmpname = ""
    # ## Read in XMP (IP, name, service, and version)
    # xx This time with beautiful soup!
    xmlsheet = BeautifulSoup(content, "lxml")

    hostsheet = xmlsheet.find_all("host")
    for host in hostsheet:
        # made these lines to separate searches by machine
        tmpaddr = host.find("address").get("addr")
        tmpaddr = highlightTerm(tmpaddr, tmpaddr, True)
        try:
            tmpname = host.find("hostname").get("name")
            tmpname = highlightTerm(tmpname, tmpname, True)
        except:
            tmpname = " "
        print("Finding exploits for " + tmpaddr +
              " (" + tmpname + ")")  # print name of machine
        for service in host.find_all("service"):
            terms.append(str(service.get("name")))
            terms.append(str(service.get("product")))
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
        tmpaddr = highlightTerm(host[0][0], host[0][0], True)
        tmpname = highlightTerm(host[0][1], host[0][1], True)
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


def run():
    """ Main function of script. hooks rest of functions
    """

    # global variables brought down

    if (len(argv) == 1 and os.sys.stdin.isatty()):
        parser.print_help()  # runs if given no arguements
        return

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
    elif parseArgs.nmap != None:
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
    searchsploitout()


run()
