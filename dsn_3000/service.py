# -*- conding: utf-8 -*-
#!/usr/bin/env python3


import asyncio
import logging
import struct
import time


log = logging.getLogger(__name__)


class EchoServerProtocol(asyncio.Protocol):
    def __init__(self, master):
        self.master = master

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.info('Connection from {}'.format(peername))
        self.transport = transport
        self.master.send_data(transport)

    def data_received(self, data):
        log.info('Data received: {!r}'.format(data))
        self.master.received(data)

        # log.info('Close the client socket')
        # self.transport.close()


class DnsServer:

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()

        self.connected = None
        self.transport = None
        self.loop.create_task(self._do_connect())

    async def _do_connect(self):
        try:
            server = await self.loop.create_server(
                lambda: EchoServerProtocol(self),
                self.host, self.port)
            self.connected = True
            log.info(f'Serving on {server.sockets[0].getsockname()}')
        except Exception as e:
            log.error(f'{e}')

    def received(self, data):
        res = b'\x01\x00\x04D3K\xc0\xa8\x00\x9e\x18\x8b\x01\x00\x01\xf6\x01\x1d\x00\x00\x00\x00\x00\xb6'
        if data != res:
            return
        message = b'\x04\x0A\x01\x00\x06\x00\x00\x00\x00\x09'
        if self.transport:
            self.transport.write(message)
            log.info('Data sent: {!r}'.format(message))

    def send_data(self, transport):
        self.transport = transport

    def start(self):
        self._auto_loop()

    def _auto_loop(self):
        message = b'\x04\x0A\x01\x00\x06\x00\x00\x00\x00\x09'
        if self.transport:
            self.transport.write(message)
            log.info('Data sent: {!r}'.format(message))
        self.loop.call_later(5, self._send_dirty)


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
    dns_server = DnsServer('0.0.0.0', 8192, loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close()
