#!/usr/bin/python
from sys import argv

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

# RC info

progname = argv[0]
files_array = []
name_array = []
git_array = []


def scrapeRC():
    divider = []
    settings = open(".searchsploit_rc").read().split("\n")
    for i in range(len(settings)):
        if(i[0] == "#"):
            continue
        divider = i.split(" ")
        if divider[0] == "files_array":
            files_array.append(divider[1])
        elif divider[0] == "name_array":
            name_array.append(divider[1])
        elif divider[0] == "git_array":
            git_array.append(divider[1])


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

# def update():

"""def update():
    arraylength = len(files_array)
    for i in range(len(arraylength)):
        # Check to see if we already have the value
        if (package_array[i] not in tmp_package[*]):
            continue

        # Else save all the information
        tmp_git += git_array[i]
        tmp_path += path_array[i]
        tmp_package += package_array[i]

    # Loop around all the new arrays
    arraylength = len(tmp_git)
    for i in range(len(arraylength)):
        git = tmp_git[i]
        path = tmp_path[i]
        package = tmp_package[i]

        # Update from the repos (e.g. Kali)
        dpkg - l "${package}" 2 > /dev/null > /dev/null
        if [["$?" == "0"]]
        then
        updatedeb "${package}"
        else
        # Update from homebrew (e.g. OSX)
        brew 2 > /dev/null > /dev/null
        if [["$?" == "0"]]
        then
        # This only really only updates "./searchsploit". The rest (can) come via git as its updated more frequently
        updatedbrew "${package}"
        fi

        # Update via Git
        updategit "${package}" "${path}" "${git}"
        fi
    done

    # Done
    exit 6
 """
