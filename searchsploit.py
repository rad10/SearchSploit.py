#!/usr/bin/env python3
from sys import argv
import os
from bs4 import BeautifulSoup

# Default options
CLIPBOARD = False
COLOUR = True
EDBID = False
EXACT = False
EXAMINE = False
FILEPATH = True
GETPATH = False
JSON = False
MIRROR = False
OVERFLOW = False
SCASE = False
VERBOSE = False
WEBLINK = False
XML = False
TITLE = False
COLOUR_TAG = ""
TAGS = ""
SEARCH = ""
EXCLUDE = ""
CASE_TAG_GREP = "-i"
CASE_TAG_FGREP = "tolower"
AWK_SEARCH = ""


terms = []
args = []


# RC info

progname = argv[0]
files_array = []
name_array = []
path_array = []
git_array = []


def scrapeRC():
    divider = []

    try:
        if(SETTINGS_LOC != ""):
            settings = open(SETTINGS_LOC, "r").read().split("\n")
        else:
            settings = open(".searchsploit_rc", "r").read().split("\n")
    except:
        settings = open("~/.searchsploit_rc", "r").read().split("\n")
    for i in settings:
        if(i == "" or i[0] == "#"):
            continue
        divider = i.split(" ")
        if divider[0] == "files_array":
            files_array.append(divider[1])
        elif divider[0] == "name_array":
            name_array.append(divider[1])
        elif divider[0] == "path_array":
            path_array.append(divider[1])
        elif divider[0] == "git_array":
            git_array.append(divider[1])
        elif divider[0] == "git_user":
            if divider[1] == "_":
                git_user = ""
            else:
                git_user = divider[1]


scrapeRC()
# Usage info


def usage():
    print("  Usage: ${progname} [options] term1 [term2] ... [termN]")
    print("")
    print("==========")
    print(" Examples ")
    print("==========")
    print("  ${progname} afd windows local")
    print("  ${progname} -t oracle windows")
    print("  ${progname} -p 39446")
    print("  ${progname} linux kernel 3.2 --exclude=\"(PoC)|/dos/\"")
    print("  ${progname} linux reverse password")
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
    cwd = os.getcwd()
    path = ""
    for i in range(len(files_array)):
        path = path_array[i]
        print("[i] Path: " + path_array[i])
        print("[i] Git Pulling: " + name_array[i] + " ~ " + path_array[i])

        # update via git
        os.chdir(path)  # set path to repos directory
        os.system("git pull --rebase")
        print("[i] Git Pull Complete")
    os.chdir(cwd)
    return


def drawline():
    rows, cols = os.popen("stty size").read().split()
    line = ""
    for i in range(int(cols)):
        line += "-"
    print(line)


def drawline(lim):
    line = ""
    col = int(os.popen("stty size").read().split()[1])
    for i in range(lim):
        line += "-"
    line += "+"
    while len(line) < col:
        line += "-"
    print(line)


def separater(line1, line2):
    print(line1 + " | " + line2)


def separater(lim, line1, line2):
    if (len(line1) >= lim):
        line1 = line1[:lim-1]
    while len(line1) <= lim:
        line1 += " "
    if '\033[91m' in line1 and '\033[0m' not in line1:
        line1 += '\033[0m'
    col = int(os.popen("stty size").read().split()[1])
    if(len(line2) >= col-lim):
        line2 = line2[:lim-1]
    if '\033[91m' in line2 and '\033[0m' not in line2:
        line2 += '\033[0m'
    print(line1 + " | " + line2)


def validTerm(argsList):
    invalidTerms = ["microsoft", "microsoft windows", "apache", "ftp",
                    "http", "linux", "net", "network", "oracle", "ssh", "unknown"]
    argsList.sort()
    for i in range(len(argsList)):
        if (argsList[i] in invalidTerms):
            argsList.pop(i)
            # Issues, return with something
            print(
                "[-] Skipping term: %s   (Term is too general. Please re-search manually:", i)
    for i in range(len(argsList)-1):
        if (argsList[i] == argsList[i + 1]):
            argsList.pop(i)
            --i
    return argsList


def highlightTerm(line, term):
    try:
        part1 = line[:line.lower().index(term)]
        part2 = line[line.lower().index(
            term): line.lower().index(term) + len(term)]
        part3 = line[line.lower().index(term) + len(term):]
        line = part1 + '\033[91m' + part2 + '\033[0m' + part3
    except:
        line = line
    return line


def searchdb(path="", terms=[], cols=[]):
    searchTerms = []
    tmphold = []
    db = open(path, "r").read().split('\n')
    for lines in db:
        for term in terms:
            if not term in lines:
                continue
        else:
            for i in cols:
                space = lines.split(",")
                tmphold.append(space[i])
            searchTerms.append(tmphold)
            tmphold = []
    return searchTerms


def searchdb(path="", terms=[], cols=[], lim=-1):
    searchTerms = []
    tmphold = []
    db = open(path, "r").read().split('\n')
    for lines in db:
        for term in terms:
            if term not in lines.lower():
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
    # ## Used in searchsploitout/nmap's XML

    # if(len(argv) == 1):
        # return
    args.append("-t")
    if (JSON):
        args.append("--json")
    if(OVERFLOW):
        args.append("--overflow")
    if(WEBLINK):
        args.append("--www")
    if(COLOUR):
        args.append("--colour")
    if(EDBID):
        args.append("--id")

    # xx validating terms
    validTerm(terms)
    if JSON:
        # TODO: finish json format
        return

    # xx building terminal look
    col = int(os.popen("stty size").read().split()[1])
    lim = int((col - 3)/2)
    query = []
    for i in range(len(files_array)):
        if EDBID:
            query = searchdb(path_array[i] + "/" +
                             files_array[i], terms, [2, 0])
        elif TITLE:
            query = searchdb(path_array[i] + "/" + files_array[i], terms, [2])
        elif WEBLINK:
            query = searchdb(path_array[i] + "/" +
                             files_array[i], terms, [2, 1, 0])
        else:
            query = searchdb(path_array[i] + "/" +
                             files_array[i], terms, [2, 1])

        if len(query) == 0:
            print(name_array[i] + ": No Results")
            continue
        drawline(lim)
        separater(col/4, name_array[i] + " Title", "Path")
        separater(col/4, "", path_array[i])
        drawline(lim)
        if TITLE:
        for lines in query:
                if COLOUR:
                    for term in terms:
                        lines[0] = highlightTerm(lines[0], term)
                print(lines[0])
        else:
            for lines in query:
            if WEBLINK:
                lines[1] = "https://www.exploit-db.com/" + \
                    lines[1][:lines[1].index("/")] + "/" + lines[2]
            if COLOUR:
                for term in terms:
                    lines[0] = highlightTerm(lines[0], term)
                    lines[1] = highlightTerm(lines[1], term)
            if EDBID:
                # made this change so that ids get less display space
                separater(int(col * 0.8), lines[0], lines[1])
            else:
                separater(lim, lines[0], lines[1])
        drawline(lim)


def nmapxml(file):
    # Read XML file

    # ## Feedback to enduser
    print("[i] Reading: " + file)

    # hosts = []  # list of hosts and their properties
    # tmpip = ""
    # tmphostname = ""
    # tmpname = ""
    # tmpservice = ""
    # ## Read in XMP (IP, name, service, and version)
    # xx This time with beautiful soup!
    xmlsheet = BeautifulSoup(open(file, "r").read(), "lxml")

    hostsheet = xmlsheet.find_all("host")
    for host in hostsheet:
        # tmpip = host.find("address").get("addr")
        # tmphostname = host.find("hostname").get("name")
        for service in host.find_all("service"):
            terms.append(service.get("name"))
            terms.append(service.get("product"))
            terms.append(service.get("version"))
    validTerm(terms)


def cpFromDb(path, id):
    db = open(path, "r").read().split('\n')
    for lines in db:
        if lines.split(",")[0] == str(id):
            return lines.split(",")
    return []


def findExploit(id):
    exploit = []
    for i in range(len(files_array)):
        exploit = cpFromDb(path_array[i] + "/" + files_array[i], id)
        if exploit == []:
            continue
        else:
            return i, exploit


def path(id):
    file, exploit = findExploit(id)
    return path_array[file] + "/" + exploit[1]


def mirror(id):
    ind, exploit = findExploit(id)
    absfile = path_array[ind]

    currDir = os.getcwd()
    inp = open(absfile + "/" + exploit[1], "rb").read()
    out = open(currDir + "/" + exploit[1].split("/")[-1], "wb")
    out.write(inp)
    return


def examine(id):
    ind, exploit = findExploit(id)
    if exploit[1].split(".")[1] == "pdf":
        os.system("firefox " + path_array[ind] + "/" + exploit[1])
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


def run():
    if (len(argv) == 1):
        usage()
        return
    args = argv[1:]
    for i in range(1, len(argv[1:]) + 1):
        if (argv[i] == "-h" or argv[i] == "--help"):
            usage()
            return
        elif (argv[i] == "-j" or argv[i] == "--json"):
            global JSON
            JSON = True
        elif (argv[i] == "-m" or argv[i] == "--mirror"):
            mirror(argv[i + 1])
            return
        elif(argv[i] == "-o" or argv[i] == "--overflow"):
            global OVERFLOW
            OVERFLOW = True
        elif(argv[i] == "-p" or argv[i] == "--path"):
            path(argv[i + 1])
            return
        elif(argv[i] == "-t"or argv[i] == "--title"):
            global TITLE
            TITLE = True
        elif(argv[i] == "-u"or argv[i] == "--update"):
            update()
            return
        elif(argv[i] == "-w"or argv[i] == "--www"):
            global WEBLINK
            WEBLINK = True
        elif(argv[i] == "-x"or argv[i] == "--examine"):
            examine(argv[i + 1])
            return
        elif(argv[i] == "--colour"):
            global COLOUR
            COLOUR = False
        elif(argv[i] == "--id"):
            global EDBID
            EDBID = True
        elif(argv[i] == "--nmap"):
            nmapxml(argv[i+1])
            return
        else:
            terms.append(argv[i])
    searchsploitout()


run()
