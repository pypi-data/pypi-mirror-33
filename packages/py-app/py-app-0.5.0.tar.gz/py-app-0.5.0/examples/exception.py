import getopt
import sys

import app.log

foreground = True
opts, args = getopt.getopt(sys.argv[1:], "f")
for opt, arg in opts:
    if opt == '-f':
        foreground = False

app.log.init(foreground = foreground)

try:
    1 / 0
except:
    app.log.exception("here...")

try:
    3 / 0
except:
    app.log.exception("fail %s", 6, 7)
