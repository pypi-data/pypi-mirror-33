import time
import getopt
import sys

import app.log

procname = None
foreground = False
logfile = None

opts, args = getopt.getopt(sys.argv[1:], "-df:p:")
for opt, arg in opts:
    if opt == '-d':
        foreground = True
    elif opt == '-f':
        logfile = arg
    elif opt == '-p':
        procname = arg


app.log.init(procname = procname,
             foreground = foreground,
             logfile = logfile)

app.log.info("starting")

for i in range(10):
    app.log.info("%d...", i)
    time.sleep(1)

app.log.info("done")
