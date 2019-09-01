#!/usr/bin/python
from sys import argv
import os

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
    settings = open(".searchsploit_rc").read().split("\n")
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

        # update via git
        os.chdir(path)  # set path to repos directory
        os.system("git pull --rebase")
    os.chdir(cwd)
    return


def drawline():
    rows, cols = os.popen("stty size").read().split()
    print(rows, cols)
    line = ""
    print(cols)
    for i in range(int(cols)):
        line += "-"
    print(line)


def validTerm(argsList):
    invalidTerms = ["microsoft", "microsoft windows", "apache", "ftp",
                    "http", "linux", "net", "network", "oracle", "ssh", "unknown"]
    for i in range(len(argsList)):
        if (argsList[i] in invalidTerms):
            argsList.pop(i)
            # Issues, return with something
            print(
                "[-] Skipping term: %s   (Term is too general. Please re-search manually:", i)
    return argsList

