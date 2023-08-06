import time
import getopt
import sys

import app.log
import app.run

pidfile = None

opts, args = getopt.getopt(sys.argv[1:], "p:")
for opt, arg in opts:
    if opt == '-p':
        pidfile = arg

if args:
    if args[0] == 'stop':
        app.run.stop(pidfile)
    elif args[0] == 'kill':
        app.run.kill(pidfile)
else:
    app.log.init()
    app.run.daemon(pidfile)

    app.log.info("starting %s", app.log.procname())
    for i in range(20):
        app.log.info("%d...", i)
        time.sleep(1)
    app.log.info("done")
