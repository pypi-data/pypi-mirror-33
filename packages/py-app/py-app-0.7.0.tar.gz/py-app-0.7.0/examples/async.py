import itertools
import asyncio

import app.log
import app.async

def coro(name, period):
    for n in itertools.count():
        app.log.info("%s: %d", name, n)
        if (name, n) == ("task C", 4):
            app.async.stop()
        yield from asyncio.sleep(period)

tasks = []

def main():
    app.log.info("starting")

    tasks.append(asyncio.ensure_future(coro("task A", 1)))
    tasks.append(asyncio.ensure_future(coro("task B", 1.3)))
    tasks.append(asyncio.ensure_future(coro("task C", 1.7)))

    try:
        yield from asyncio.sleep(10)
    except asyncio.CancelledError:
        app.log.info("interrupted")

    for n, task in enumerate(tasks):
        app.log.info("cancelling task %d", n)
        task.cancel()

    app.log.info("done")

app.log.init(foreground = True)
app.async.start(main)
