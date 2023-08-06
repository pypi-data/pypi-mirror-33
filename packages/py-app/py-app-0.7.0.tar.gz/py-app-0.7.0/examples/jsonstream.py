import itertools
import asyncio

import app.log
import app.async

class Client(app.async.JSONStreamProtocol):

    def received(self, obj):
        app.log.info("received: %r", obj)
        self.send(obj)

def main():
    app.log.info("starting")

    loop = asyncio.get_event_loop()
    server = yield from loop.create_server(Client,
                                           host = "127.0.0.1",
                                           port = 5554)

    try:
        while True:
            yield from asyncio.sleep(30)
    except asyncio.CancelledError:
        app.log.info("interrupted")

    server.close()

    app.log.info("done")

app.log.init(foreground = True)
app.async.start(main)
