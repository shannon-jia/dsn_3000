#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import logging
import struct


log = logging.getLogger(__name__)


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, master):
        self.master = master

    def connection_made(self, transport):
        self.master.connected = True
        print(self.master.message)
        if self.master.message:
            transport.write(self.master.message)
            log.info('Data sent: {!r}'.format(self.master.message))

    def data_received(self, data):
        log.info('Data received: {!r}'.format(data))

    def connection_lost(self, exc):
        self.master.connected = None
        log.info('The server closed the connection')



class Dns_3000:

    def __init__(self, host, port, message, loop):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()

        self.connected = None
        self.transport = None
        self.message = message

        self.loop.create_task(self._do_connect())

    async def _do_connect(self):
        while True:
            await asyncio.sleep(1)
            if self.connected:
                continue
            try:
                transport, protocol = await self.loop.create_connection(
                    lambda: EchoClientProtocol(self),
                    self.host,
                    self.port)
                log.info('Connection create on {}'.format(transport))
                self.transport = transport
            except OSError:
                log.error('Server not up retrying in 5 seconds...')
            except Exception as e:
                log.error('Error when connect to server: {}'.format(e))

    def parse_data(self, data):
        pass

    def is_invalid(self, mesg):
        pass

    def solve_dirty(self, data):
        pass


if __name__ == "__main__":
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # log the things
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    loop = asyncio.get_event_loop()
    message = b'\x04\x00\x04D3K\xc0\xa8\x00\x9e\x18\x8b\x01\x00\x10\xf6\x01\x01\x02\x00\x00\x00\x00\xbc'
    dns = Dns_3000('192.168.1.157', 8192, message, loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
