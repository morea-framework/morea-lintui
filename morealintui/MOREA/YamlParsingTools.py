import re

from morealintui.Toolbox.toolbox import bold, CustomException

__author__ = 'casanova'

# Passing end=-1 means "everything after
def get_contents_at_dash_marker(path, start, end):
    contents = ""
    f = open(path, "r")
    separator_seen = 0
    for line in f:
        if re.match("\s*---.*", line) is not None:
            separator_seen += 1
            continue
        if separator_seen == start:
            contents += line
        elif separator_seen == end:
            break
    f.close()
    return contents


def validate_basic_file_structure(path):
    f = open(path, "r")
    separator_seen = 0
    for line in f:
        if re.match("\s*---.*", line) is not None:
            separator_seen += 1
    f.close()
    return separator_seen >= 2


def get_non_yaml_contents(path):
    return get_contents_at_dash_marker(path, 2, -1)


def get_raw_front_matter(path):
    return get_contents_at_dash_marker(path, 1, 2)


def commentify(string, parse_comments):
    """ This  is a hack to deal with comments. It's very limited and DOES NOT SUPPORT END-OF-LINE COMMENTS,
    which will be obliterated by this script (it prints warning). One solution could be to use
    the ruamel.yaml package, but it comes with other issues that I am too lazy to deal with right now. Importantly,
    it's not clear whether it can handle the more important non-end-of-line comments. """

    if not parse_comments:
        return string

    # print "STRING = ", string

    # Remove full-line comments
    # if re.match('\s*#[^\-:]*$', string) is not None:
    #    return None

    # Ignore full-line comments, as they should be continuations from previous lines!
    # (string, count) = re.subn('^\s*#(?P<content>[^\-:]*$)', r' \g<content>', string)
    # print "NOW: ", string

    # Look for end-of-line comments, remove them and set the warning flag
    # (string, count) = re.subn(r'(?P<start>^.*[\-:].*)\s(?P<comment>#.*)', r'\g<start>', string)
    # eol_comment = eol_comment or (count > 0)

    # Look for " - stuff" and replacing with "  -"
    (string, count) = re.subn(r'^\s*-\s*', r'  - ', string)

    # Look for "# - stuff" and replacing with "  - __COMMENTEDOUT__stuff"
    (string, count) = re.subn(r'(?P<start>^\s*)[\s#]*#(\s*)-(\s*)(?P<end>.*)', '  - ' + '__COMMENTEDOUT__' +
                              unicode(commentify.counter) + '__' + r'\g<end>', string)
    if count == 1:
        commentify.counter += 1
    elif count > 1:
        raise CustomException('Commentifying error')

    # Look for "# stuff" and replacing with "__COMMENTEDOUT__stuff"
    (string, count) = re.subn(r'(?P<start>^\s*)[\s#]*#(\s*)(?P<end>.*)', r'__COMMENTEDOUT__' +
                              unicode(commentify.counter) + '__' + r'\g<end>', string)
    if count == 1:
        commentify.counter += 1
    elif count > 1:
        raise CustomException('Commentifying error')

    return string


commentify.counter = 0


def batch_quoted_character_replacement(string, src, dst):
    num_seen_quotes = 0
    sanitized = ""

    for c in string:
        if c == '"':
            num_seen_quotes += 1
        if num_seen_quotes > 2:
            raise CustomException("  Incoherent quotes!")
        if num_seen_quotes == 2:
            num_seen_quotes = 0
        if c == src and num_seen_quotes == 1:
            sanitized += dst
        else:
            sanitized += c
    return sanitized


def remove_redundant_hashes(string):
    new = ""
    for l in string.splitlines():
        (newl, count) = re.subn(r'^#(\s*#)*', r' #', l)
        (newl, count) = re.subn(r' #(\s*#)*', r' #', newl)

        new += newl + "\n"
    return new


def remove_leading_and_trailing_spaces(string):
    new = ""
    for l in string.splitlines():
        # Leading
        (newl, count) = re.subn(r'^\s\s*', r' ', l)
        # Leading in from of a dash
        (newl, count) = re.subn("^\s#", "#", newl)
        # Trailing
        (newl, count) = re.subn(r'\s*$', r'', newl)
        new += newl + "\n"
    return new


def remove_all_end_of_line_comments(string):
    eol_comment_found = False
    new = ""
    for l in string.splitlines():
        # Look for end-of-line comments, remove them and set the warning flag
        newl = l
        count = 0
        while True:
            (newl, count) = re.subn(r'(?P<start>^.*[^\s]\s\s*)#.*', r'\g<start>', newl)
            if count == 0:
                break
        eol_comment_found = eol_comment_found or (count > 0)
        new += newl + "\n"

    return new, eol_comment_found


def make_all_comments_one_liners(string):
    previous_line_is_a_comment = False
    previous_line_dangling_quote = False
    seen_quotes = 0
    new = ""
    for l in string.splitlines():

        # print "--> l=", l

        # Determine pattern of string
        commented_out_declaration = False
        commented_out_dangling_line = False
        if re.search('^\s*(#\s*)(#\s*)*.*[^\s].*\s*:.*', l) is not None:
            commented_out_declaration = True
        elif re.search('^\s*(#\s*)(#\s*)*-.*', l) is not None:
            commented_out_declaration = True
        elif re.search('^\s*(#\s*)(#\s*)*.*', l) is not None:
            commented_out_dangling_line = True

        # Update number of quotes seen so far
        seen_quotes += len(re.findall('"', l))

        # print "commented_out_decl: ", commented_out_declaration, \
        #       "  commented_out_dangling:", commented_out_dangling_line, \
        #       "seen_quotes =", seen_quotes
        if commented_out_declaration:
            if new == "":
                new += l
            else:
                new += "\n" + l
            previous_line_dangling_quote = (seen_quotes % 2) == 1
            previous_line_is_a_comment = True
            continue

        if commented_out_dangling_line:
            if previous_line_dangling_quote and not previous_line_is_a_comment:
                (afterdash, count) = re.subn('^\s*(?P<content>#.*)', r'\g<content>', l)
                new += " " + afterdash
                # Keep the dangling quote
                continue
            if previous_line_is_a_comment:
                (afterdash, count) = re.subn('^\s*#(?P<spaces>\s*)(?P<content>.*)', r'\g<content>', l)
                new += " " + afterdash
                previous_line_dangling_quote = (seen_quotes % 2) == 1
                continue
            else:
                raise CustomException("    full-line comments can't be processed by this script")

        if new == "":
            new += l
        else:
            new += "\n" + l
        previous_line_is_a_comment = False
        previous_line_dangling_quote = (seen_quotes % 2) == 1

    new += "\n"

    return new


def get_commentified_front_matter(path, warnings, parse_comments):
    raw_front_matter = get_raw_front_matter(path)
    eol_comment_found = False

    # PREPROCESSING
    try:
        sanitized_front_matter = raw_front_matter

        debug = False

        if debug:
            print "\n*********  RAW  ****************\n"
            print sanitized_front_matter
            print "**********************************\n"

        if parse_comments:

            # DO A PASS TO REMOVE ALL LEADING SPACES
            sanitized_front_matter = remove_leading_and_trailing_spaces(sanitized_front_matter)

            if debug:
                print "\n*********  AFTER PASS (REMOVE LEADING SPACE) ****************\n"
                print sanitized_front_matter
                print "**********************************\n"

            # DO A PASS TO MAKE ALL COMMENTS ONE-LINERS
            sanitized_front_matter = make_all_comments_one_liners(sanitized_front_matter)

            if debug:
                print "\n*********  AFTER PASS (MAKE ALL COMMENTS ONE-LINERS)  ****************\n"
                print sanitized_front_matter
                print "**********************************\n"

            # DO A PASS TO DEAL WITH #'S AND QUOTES
            sanitized_front_matter = batch_quoted_character_replacement(sanitized_front_matter, "#", "__GENUINEHASH__")

            if debug:
                print "\n*********  AFTER PASS (SANITIZE REAL QUOTES)  ****************\n"
                print sanitized_front_matter
                print "**********************************\n"

            # DO A PASS TO REMOVE ALL REDUNDANT COMMENTS
            sanitized_front_matter = remove_redundant_hashes(sanitized_front_matter)

            if debug:
                print "\n*********  AFTER PASS (REMOVE REDUNDANT HASHES) ****************\n"
                print sanitized_front_matter
                print "**********************************\n"

            # DO A  PASS TO REMOVE ALL END-OF-LINE COMMENTS
            sanitized_front_matter, eol_comment_found = remove_all_end_of_line_comments(sanitized_front_matter)

            if debug:
                print "\n*********  AFTER 5TH PASS (REMOVE END-OF-LINE COMMENTS) ****************\n"
                print sanitized_front_matter
                print "**********************************\n"

    except CustomException as e:
        raise CustomException("    md content pre-processing error for file " + path + "\n" + str(e))

    # print "********  POST_PROCESSED *********\n"
    # print sanitized_front_matter
    # print "**********************************\n"

    # THEN GO THROUGH THE FILE LINE BY LINE
    commentified_front_matter = ""
    for l in sanitized_front_matter.splitlines():
        commentified_line = commentify(l, parse_comments)

        if commentified_line is not None:
            # try:
            #    commentified_line.decode('ascii')
            # except UnicodeDecodeError:
            #    print "NOT ASCII!"
            commentified_line = commentified_line.decode("utf-8")
            commentified_front_matter += commentified_line + "\n"

    if parse_comments:
        # DO A FINAL PASS TO "UNSANITIZE" THE HASHES
        commentified_front_matter = re.sub(r'__GENUINEHASH__', r'#', commentified_front_matter)

    if eol_comment_found and warnings:
        print bold("  Warning: end-of-line comments in file " + path + " will be lost!")

    return commentified_front_matter


def decommentify(string):
    if type(string) == int:
        return [string, 0]
    if type(string) == bool:
        return [string, 0]

    (new, count) = re.subn(r'__COMMENTEDOUT__[0-9]*__', r'', string)

    # print "IN DECOMMENTIFY(): ", string, "-->", new
    if count > 1:
        raise CustomException("Error while decommentifying...")
    if type(string) == unicode:
        new = unicode(new)
    return [new, count >= 1]


def check_for_duplicate_entries(front_matter, parse_comments):

    entries = []
    err_msg = ""
    linecount = 0
    for l in front_matter.splitlines():
        linecount += 1
        (key, count) = re.subn(r'(?P<id>^[^\s][^\'\"]*):.*', r'\g<id>', l)
        if parse_comments:
            if re.search("^__COMMENTEDOUT__", key) is not None:
                continue
        else:
            if re.search("^\s*#.*", key) is not None:
                continue
        if count == 1:
            if key in entries:
                err_msg += "  Duplicate entry '" + key + "' at line " + str(linecount) + "\n"
            entries.append(key)
        elif count > 1:
            raise CustomException("Strange error while checking for duplicate entries for line: '" + l + "'")
    if err_msg != "":
        raise CustomException(err_msg)
    return
