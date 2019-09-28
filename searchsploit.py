#!/usr/bin/env python3
from sys import argv, exit
import os

# settings
SETTINGS_LOC = ""
# This should be the only variable that you need to edit manually.
# place the file path of .searchsploit_rc so that the script can get the
# rest of the settings from anywhere


# Default options
COLOUR = True
EDBID = False
EXACT = False
JSON = False
OVERFLOW = False
WEBLINK = False
TITLE = False
IGNORE = False
CASE = False
COL = 0

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

progname = argv[0].split("/")[-1]
files_array = []  # Array options with file names
name_array = []  # Array options with database names
path_array = []  # Array options with paths to database files
git_array = []  # Array options with the git repo to update the databases


def scrapeRC():
    """ This function runs on init to get settings for all the databases used for searching
    """
    divider = []

    try:
        if(SETTINGS_LOC != ""):  # Checks if the variable is empty
            settings = open(SETTINGS_LOC, "r").read().split("\n")
        else:
            settings = open(".searchsploit_rc", "r").read().split("\n")
    except:
        try:
            settings = open(os.path.expanduser("~").replace(
                "\\", "/") + "/.searchsploit_rc", "r").read().split("\n")
            # Checks for home directory in linux/mac
        except:
            settings = open(os.getenv("userprofile").replace(
                "\\", "/") + "/.searchsploit_rc", "r").read().split("\n")
            # Checks for home directory in windows
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
    for i in range(larray):
        try:
            open(path_array[larray-i-1] + "/" + files_array[larray-i-1],
                 "r", encoding="utf8").read()
        except:
            files_array.pop(larray - i - 1)
            name_array.pop(larray - i - 1)
            path_array.pop(larray - i - 1)
            git_array.pop(larray - i - 1)
            --i


scrapeRC()


# Usage info
def usage():
    """ This function displays the manual for the program and the help function
    """
    print("  Usage: " + progname + " [options] term1 [term2] ... [termN]")
    print("")
    print("==========")
    print(" Examples ")
    print("==========")
    print("  " + progname + " afd windows local")
    print("  " + progname + " -t oracle windows")
    print("  " + progname + " -p 39446")
    print("  " + progname + " linux kernel 3.2 --exclude=\"(PoC)|/dos/\"")
    print("  " + progname + " linux reverse password")
    print("")
    print("  For more examples, see the manual: https://www.exploit-db.com/searchsploit")
    print("")
    print("=========")
    print(" Options ")
    print("=========")
    print(
        "   -c, --case     [Term]      Perform a case-sensitive search (Default is inSEnsITiVe).")
    print(
        "   -e, --exact    [Term]      Perform an EXACT match on exploit title (Default is AND) [Implies \"-t\"].")
    print(
        " -i, --ignore    [Term]     Adds any redundant term in despite it possibly giving false positives.")
    print("   -h, --help                 Show this help screen.")
    print("   -j, --json     [Term]      Show result in JSON format.")
    print(
        "   -m, --mirror   [EDB-ID]    Mirror (aka copies) an exploit to the current working directory.")
    print(
        "   -o, --overflow [Term]      Exploit titles are allowed to overflow their columns.")
    print(
        "   -p, --path     [EDB-ID]    Show the full path to an exploit (and also copies the path to the clipboard if possible).")
    print(
        "   -t, --title    [Term]      Search JUST the exploit title (Default is title AND the file's path).")
    print("   -u, --update               Check for and install any exploitdb package updates (deb or git).")
    print(
        "   -w, --www      [Term]      Show URLs to Exploit-DB.com rather than the local path.")
    print(
        "   -x, --examine  [EDB-ID]    Examine (aka opens) the exploit using \$PAGER.")
    print("       --colour               Disable colour highlighting in search results.")
    print("       --id                   Display the EDB-ID value rather than local path.")
    print(
        "       --nmap     [file.xml]  Checks all results in Nmap's XML output with service version (e.g.: nmap -sV -oX file.xml).")
    print("                                Use \"-v\" (verbose) to try even more combinations")
    print("       --exclude=\"term\"       Remove values from results. By using \"|\" to separated you can chain multiple values.")
    print("                                e.g. --exclude=\"term1|term2|term3\".")
    print("")
    print("=======")
    print(" Notes ")
    print("=======")
    print(" * You can use any number of search terms.")
    print(" * Search terms are not case-sensitive (by default), and ordering is irrelevant.")
    print("   * Use '-c' if you wish to reduce results by case-sensitive searching.")
    print("   * And/Or '-e' if you wish to filter results by using an exact match.")
    print(" * Use '-t' to exclude the file's path to filter the search results.")
    print("   * Remove false positives (especially when searching using numbers - i.e. versions).")
    print(" * When updating or displaying help, search terms will be ignored.")
    print("")
    exit(2)

# Update database check


def update():
    """ This function is used to update all the databases via github (because github is the best update system for databases this size)
    """
    cwd = os.getcwd()
    path = ""
    for i in range(len(files_array)):
        path = path_array[i]
        print("[i] Path: " + path_array[i])
        print("[i] Git Pulling: " + name_array[i] + " ~ " + path_array[i])

        # update via git
        os.chdir(path)  # set path to repos directory
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
    if OVERFLOW:
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
    db = open(path, "r", encoding="utf8").read().split('\n')
    for lines in db:
        if lines.split(",")[0] == str(id):
            return lines.split(",")
    return []


def findExploit(id):
    """ This Function uses cpFromDB to iterate through all known databases and return exploit and the database it was found in\n
    @id: EDBID used to search all known databases\n
    @return: exploit[], database path
    """
    exploit = []
    for i in range(len(files_array)):
        exploit = cpFromDb(path_array[i] + "/" + files_array[i], id)
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
    if EXACT:
        return argsList
    argsList.sort()
    argslen = len(argsList)
    for i in range(argslen):
        if (argsList[argslen-i-1].lower() in dudTerms):
            argsList.pop(argslen-i-1)
        elif (argsList[argslen-i-1].lower() in invalidTerms and not IGNORE):
            print(
                "[-] Skipping term: " + argsList[argslen-i-1] + "   (Term is too general. Please re-search manually:")
            argsList.pop(argslen-i-1)
            # Issues, return with something
        elif not CASE:
            argsList[argslen-i-1] = argsList[argslen-i-1].lower()
    argsList.sort()
    argslen = len(argsList)
    for i in range(argslen-1):
        if (argsList[argslen-i-2] == argsList[argslen-i-1]):
            argsList.pop(argslen-i-1)
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
    if EXACT:
        tmpstr = str(terms[0])
        for i in range(1, len(terms)):
            tmpstr += " " + terms[i]
        terms.clear()
        terms.append(tmpstr)
    db = open(path, "r", encoding="utf8").read().split('\n')
    for lines in db:
        if (lines != ""):
            for term in terms:
                if TITLE:
                    line = lines.split(",")[2]
                    if CASE:
                        if term not in line:
                            break
                    elif term not in line.lower():
                        break
                elif CASE:
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
    return searchTerms


def searchsploitout():
    """ Convoluted name for the display. takes the global search terms and prints out a display iterating through every database available and printing out the results of the search.
    """
    # ## Used in searchsploitout/nmap's XML

    # xx validating terms
    validTerm(terms)
    if JSON:
        # TODO: finish json format
        return

    # xx building terminal look
    # the magic number to decide how much space is between the two subjects
    lim = int((COL - 3)/2)
    query = []  # temp variable thatll hold all the results
    try:
        for i in range(len(files_array)):
            if EDBID:
                query = searchdb(path_array[i] + "/" +
                                 files_array[i], terms, [2, 0])
            elif WEBLINK:
                query = searchdb(path_array[i] + "/" +
                                 files_array[i], terms, [2, 1, 0])
            else:
                query = searchdb(path_array[i] + "/" +
                                 files_array[i], terms, [2, 1])

            if len(query) == 0:  # is the search results came up with nothing
                print(name_array[i] + ": No Results")
                continue
            drawline(lim)
            separater(COL/4, name_array[i] + " Title", "Path")
            separater(COL/4, "", path_array[i])
            drawline(lim)  # display title for every database
            for lines in query:
                if WEBLINK:  # if requesting weblinks. shapes the output for urls
                    lines[1] = "https://www.exploit-db.com/" + \
                        lines[1][:lines[1].index("/")] + "/" + lines[2]
                if COLOUR:
                    for term in terms:
                        lines[0] = highlightTerm(lines[0], term)
                        lines[1] = highlightTerm(lines[1], term)
                if EDBID:
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

    # First check whether file exists or use stdin
    try:
        content = open(file, "r").read()
    except:
        if(not os.sys.stdin.isatty()):
            content = os.sys.stdin.read()
        else:
            return True

    # stope if blank or not an xml sheet
    if content == "" or content[:5] != "<?xml":
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
    print("[i] Reading: " + highlightTerm(str(file), str(file), True))
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

    # First check whether file exists or use stdin
    try:
        content = open(file, "r").read()
    except:
        if(not os.sys.stdin.isatty()):
            content = os.sys.stdin.read()
        else:
            return False

    # Check whether its grepable
    if (content.find("Host: ") == -1 and "-oG" in content.split("\n")[0]):
        return False

    # making a matrix to contain necessary strings
    nmatrix = content.split("\n")
    for lines in range(len(nmatrix) - 1, -1, -1):
        if (nmatrix[lines].find("Host: ") == -1 or nmatrix[lines].find("Ports: ") == -1):
            nmatrix.pop(lines)
        else:
            nmatrix[lines] = nmatrix[lines].split("\t")[:-1]
            nmatrix[lines][0] = nmatrix[lines][0][6:].split(" ")
            nmatrix[lines][0][1] = nmatrix[lines][0][1][1:-1] if (len(nmatrix[lines][0][1]) > 2) else "" # pull hostname out of parenthesis
            nmatrix[lines][1] = nmatrix[lines][1][7:].split(", ")
            for j in range(len(nmatrix[lines][1])):
                nmatrix[lines][1][j] = nmatrix[lines][1][j].replace("/", " ").split()[3:]
    print(nmatrix)
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
    print(path_array[file] + "/" + exploit[1])
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
    inp = open(absfile + "/" + exploit[1], "rb").read()
    out = open(currDir + "/" + exploit[1].split("/")[-1], "wb")
    out.write(inp)
    return


def examine(id):
    """ Function used to run examine arguement
    """
    try:
    ind, exploit = findExploit(id)
    except TypeError:
        print("%s does not exist. Please double check that this is the correct id." % id)
        return
    if exploit[1].split(".")[1] == "pdf":
        os.system("firefox file:///" + path_array[ind] + "/" + exploit[1])
    else:
        os.system("pager " + path_array[ind] + "/" + exploit[1])
    print("[EDBID]:"+exploit[0])
    print("[Exploit]:" + exploit[2])
    print("[Path]:" + path_array[ind] + "/" + exploit[1])
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
    global CASE
    global EXACT
    global IGNORE
    global JSON
    global OVERFLOW
    global TITLE
    global WEBLINK
    global COLOUR
    global EDBID

    if (len(argv) == 1 and os.sys.stdin.isatty()):
        usage()  # runs if given no arguements
        return
    for i in range(1, len(argv[1:]) + 1):
        if (argv[i] == "-h" or argv[i] == "--help"):
            usage()
            return
        elif (argv[i] == "-c" or argv[i] == "--case"):
            CASE = True
        elif (argv[i] == "-e" or argv[i] == "--exact"):
            EXACT = True
        elif (argv[i] == "-i" or argv[i] == "--ignore"):
            IGNORE = True
        elif (argv[i] == "-j" or argv[i] == "--json"):
            JSON = True
        elif (argv[i] == "-m" or argv[i] == "--mirror"):
            mirror(argv[i + 1])
            return
        elif(argv[i] == "-o" or argv[i] == "--overflow"):
            OVERFLOW = True
        elif(argv[i] == "-p" or argv[i] == "--path"):
            path(argv[i + 1])
            return
        elif(argv[i] == "-t"or argv[i] == "--title"):
            TITLE = True
        elif(argv[i] == "-u"or argv[i] == "--update"):
            update()
            return
        elif(argv[i] == "-w"or argv[i] == "--www"):
            WEBLINK = True
        elif(argv[i] == "-x"or argv[i] == "--examine"):
            examine(argv[i + 1])
            return
        elif(argv[i] == "--colour"):
            COLOUR = False
        elif(argv[i] == "--id"):
            EDBID = True
        elif(argv[i] == "--nmap"):
            try:
                if(argv[i+1][0] != "-"):
                    nmapxml(argv[i+1])
                else:
                    usage()
            except:
                if(os.sys.stdin.isatty() == False):
                    nmapxml()
                else:
                    usage()
            return
        else:
            terms.append(argv[i])

    if (not os.sys.stdin.isatty()):
        text = str(os.sys.stdin.read())
        terms.extend(text.split())
    if terms == []:
        usage()  # if no actual terms were made just arguements, then exit
        return

    # Colors for windows
    if COLOUR and os.sys.platform == "win32":
        try:
            import colorama
        except ImportError:
            print(
                "You do not have colorama installed. if you want to run with colors, please run:")
            print(
                "\"pip install colorama\" in your terminal so that windows can use colors.")
            print("Printing output without colors")
            COLOUR = False
        else:
            colorama.init()
    searchsploitout()


run()
