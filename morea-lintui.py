import copy
import unittest
from MOREA.MoreaContent import MoreaContent
import shlex
import subprocess
from Testing.CustomTestRunner import CustomTestRunner
from Toolbox.toolbox import *
import argparse
import os
import TUI.TUI


__author__ = 'casanova'

"""
This function invokes jekyll to make sure that everything "compiles".
Annoyingly, in the case of YAML errors, jekyll still returns error code 0,
in the sense that the site is built but something went wrong (but is ignored)
in the YAML parsing. This can only (I think) be detected by looking at whether
the word 'Error' occurs in the stderr of jekyll. Pretty broken, really. In fact,
as a user of jekyll I've missed those errors countless times because I blinked
and didn't see them go by on my terminal (even though they show up yellow-ish).
This issue is discussed at:
    https://github.com/jekyll/jekyll/issues/1907
and may be fixed in  jekyll v3.0.xx (currently beta)? I am running 2.5.3
"""


def pre_validate_site(morea_root):
    valid = True
    err_msg = ""

    print "  Using jekyll to generate tmp site..."
    tmp_site = "/tmp/morea-ncursed-site/"
    command = "jekyll build --source " + morea_root + "/.. --destination " + tmp_site

    # Check that we can run jekyll with a zero exit code
    stdout = ""
    stderr = ""
    try:
        proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
    except Exception, msg:
        err_msg += "jekyll returns a non-zero error code\n"
        valid = False

    # Removing tmp site in case it was generated (even if it wasn't :)
    subprocess.call(("/bin/rm -rf " + tmp_site).split())

    # Check that no error was generated in the stderr (and stdout, since we're at it)
    for line in stderr.splitlines() + stdout.splitlines():
        if "Error" in line:
            valid = False
        if "Error" in line and "Exiting" not in line:
            err_msg += "    " + yellow(line.lstrip()) + "\n"

    if not valid:
        raise CustomException(err_msg)

    return


""" This function prints a "splash" screen
"""

def print_welcome_screen():
    print(chr(27) + "[2J")
    print_as_paragraph(green, "- This script is picky about .md syntax, so you "
                              "can expect many errors and warnings that you'll have to fix "
                              "(for good measure this script can also run jekyll as"
                              " an initial validation step if"
                              " the --run-jekyll command-line argument is provided).")
    print ""
    print_as_paragraph(green, "- If the --parse-comments command-line argument is provided "
                              "the script will parse all comments, thus being picky about "
                              "commented-out md content. In particular,"
                              "floating full-line comments are not supported.")
    print "\n"
    if not args.tui:
        print_as_paragraph(green, "- This script will modify your .md files based on your interaction with "
                                  "the interface. Note that cosmetic changes will occur as well (e.g., white "
                                  "spacing, indentation), making your files more uniform. Bend to this "
                                  " script's will!")
        print "\n"

        print_as_paragraph(green, "- Resizing the terminal window will not be a good idea (unless you"
                                  " get an error that tells you to do so due to it being too small).")
        print "\n"

    raw_input(bold("Press ENTER to continue, ^C to abort --"))
    print(chr(27) + "[2J")


######################################################################################
######################################################################################

# Parse command-line arguments
parser = argparse.ArgumentParser(description='MOREA content management interface.')
parser.add_argument('--tui', help='launch the TUI after validating MORE content',
                    action='store_true')
parser.add_argument('--run-jekyll', help='run jekyll as a first validation step',
                    action='store_true')
parser.add_argument('--test', help='only run the test suite',
                    action='store_true')
parser.add_argument('--parse-comments', help='parse/handle commented-out content',
                    action='store_true')
parser.add_argument('--no-splash', help="don't display initial warning screen",
                    action='store_true')

args = parser.parse_args()

if args.test:
    print green("Running test suite:")
    dirname, filename = os.path.split(os.path.abspath(__file__))
    suite = unittest.TestLoader().discover(dirname)
    if (suite.countTestCases() == 0):
        print "  Not detecting any unit tests... aborting\n"
        exit(1)
    else:
        CustomTestRunner().run(suite)
    exit(0)


# Determine where the morea content is
root = ""
if os.path.isdir("./master/src/morea/"):
    root = "./master/src/morea/"
elif os.path.isdir("./src/morea/"):
    root = "./src/morea/"
else:
    print_as_paragraph(red, "\nCouldn't find ./master/src/morea/ or ./src/morea/ directory... Aborting")
    exit(1)


# Print warning/disclaimer screen
if not args.no_splash:
    print_welcome_screen()

# Make sure that MOREA content is not broken
if args.run_jekyll:
    print green("Pre-validating site content with jekyll...")
    try:
        pre_validate_site(root)
    except CustomException as e:
        print yellow(str(e))
        print_as_paragraph(red, "MOREA site seems broken based on running morea-run-local.sh. "
                                "Fix the above error(s) and re-run this script."
                                "(run morea-run-local.sh for possibly more detailed error reports)")
        exit(1)

# Create a morea content object
morea_content = MoreaContent()

# Acquire and further validate MOREA content
print green("Acquiring MOREA content...")
try:
    morea_content.acquire_all_content(root, args.parse_comments)
except CustomException as e:
    print yellow(str(e))
    print_as_paragraph(red, "MOREA .md files seem to have YAML issues. "
                            "Fix the above error(s) and re-run this script "
                            "  (which is not as lenient as morea-run-local.sh, for good reasons).")
    exit(1)

# Checking MOREA content
print green("\nValidating MOREA content...")
try:
    morea_content.check()
except CustomException as e:
    print yellow(unicode(e))
    print_as_paragraph(red, "MOREA .md files seem to have issues. Fix the above error(s) "
                            "and re-run this script (which is not as lenient as morea-run-local.sh, "
                            "for good reasons).")
    exit(1)

if not args.tui:
    print(bold("\n-- MOREA content validated --\n"))
    exit(0)

raw_input(bold("\n\nPress ENTER to launch the interface, ^C to abort --"))
print(chr(27) + "[2J")

# Launch the ncurses UI
if args.tui:
    tui = TUI(copy.deepcopy(morea_content))
    updated_morea_content = tui.run()
    updated_morea_content.save()
