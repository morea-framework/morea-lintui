from MOREA.YamlParsingTools import get_raw_front_matter

__author__ = 'casanova'

import sys
import yaml

if len(sys.argv) != 2:
    print "Usage: " + sys.argv[0] + " <.md file path>\n"
    exit(1)

try:
    print yaml.load(get_raw_front_matter(sys.argv[1]))
except Exception as e:
    print str(e)
