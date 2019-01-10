#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
import logging
import struct


log = logging.getLogger(__name__)


class Dns_3000:

    """Main module."""

    TYPE = 4
    LOGO = b'D3K'
    HEAD_LENGTH = 11
    TOGGLE_CHANNEL = b'\x8A'
    CONTROL_CHANNEL = b'\x8B'
    LEVEL = 1
    RETAIN = b''

    TOGGLE_COMMAND_FMT = '<sH2sH'
    CLOUD_CONTROL_FMT = '<sHBHB5s'
    MANUAL_CONTROL_FMT = '<sHsHBB4s'

    dispatch = {
        'PAN': {
            'cmd': b'\x10',
            'byte4': {
                'stop': 0,
                'left': 1,
                'right': 2
            }
        },
        'TILT': {
            'cmd': b'\x11',
            'byte4': {
                'stop': 0,
                'up': 1,
                'down': 2
            }
        },
        'ZOOM': {
            'cmd': b'\x12',
            'byte4': {
                'stop': 0,
                'in': 1,
                'out': 2
            }
        },
        'Focus': {
            'cmd': b'\x13',
            'byte4': {
                'stop': 0,
                'near': 1,
                'far': 2
            }
        },
        'IRIS': {
            'cmd': b'\x14',
            'byte4': {
                'stop': 0,
                'open': 1,
                'close': 2
            }
        },
        'WASH': {
            'cmd': b'\x15',
            'byte4': {
                'stop': 0,
                'work': 1
            }
        },
        'WIPE': {
            'cmd': b'\x16',
            'byte4': {
                'stop': 0,
                'work': 1
            }
        }
    }

    DATA_LEN = 10

    def __init__(self, ip='192.168.0.158'):
        self.ip = ip
        self.command_code = 0

    def toggle_command(self, camera):
        try:
            return self.add_check(self.TOGGLE_COMMAND_FMT,
                                  self.TOGGLE_CHANNEL,
                                  self.LEVEL,
                                  self.RETAIN,
                                  camera)
        except Exception as e:
            log.error(f'{e}')

    def call_preset(self, camera, preset):
        cmd = 1
        try:
            return self.add_check(self.CLOUD_CONTROL_FMT,
                                  self.CONTROL_CHANNEL,
                                  self.LEVEL,
                                  cmd,
                                  camera,
                                  preset,
                                  self.RETAIN)
        except Exception as e:
            log.error(f'{e}')

    def set_preset(self, camera, preset):
        cmd = 2
        try:
            return self.add_check(self.CLOUD_CONTROL_FMT,
                                  self.CONTROL_CHANNEL,
                                  self.LEVEL,
                                  cmd,
                                  camera,
                                  preset,
                                  self.RETAIN)
        except Exception as e:
            log.error(f'{e}')

    def manual_control(self, action, camera, direction, speed):
        try:
            cmd, byte4 = self._deal_control(action, direction)
            return self.add_check(self.MANUAL_CONTROL_FMT,
                                  self.CONTROL_CHANNEL,
                                  self.LEVEL,
                                  cmd,
                                  camera,
                                  byte4,
                                  speed,
                                  self.RETAIN)
        except Exception as e:
            log.error(f'{e}')

    def _deal_control(self, action, direction):
        _box = self.dispatch.get(action.upper())
        cmd = _box.get('cmd')
        byte4 = _box.get('byte4').get(direction)
        return cmd, byte4

    def _deal_code(self):
        if self.command_code < 0 or self.command_code > 200:
            self.command_code = 1
        else:
            self.command_code += 1
        return self.command_code

    def _deal_ip(self):
        _ip_list = self.ip.split('.')
        ip_tup = (int(i) for i in _ip_list)
        return ip_tup

    def _build(self, message):
        length = self.HEAD_LENGTH + len(message) + 1
        s = struct.Struct('<HB3sBBBBB')
        head = s.pack(self._deal_code(),
                      self.TYPE, self.LOGO,
                      *self._deal_ip(),
                      length)
        _command = head + message
        _xor = 0
        for i in _command:
            _xor ^= i
        command = _command + struct.pack('<B', _xor)
        return command

    def add_check(self, fmt, *args, **kwargs):
        s = struct.Struct(fmt)
        message = s.pack(*args)
        return self._build(message)

    def is_invalid(self, data):
        if len(data) != self.DATA_LEN:
            return True
        if data[1] != len(data):
            return True
        if data[0] != self.TYPE:
            return True
        (_code, _spare) = struct.unpack('<H3s', data[2:4] + data[6:-1])
        _xor = 0
        for i in data[:-1]:
            _xor ^= i
        if _xor != data[-1]:
            return True
        return False

    def received(self, data):
        if self.is_invalid(data):
            return None
        return self.unpack_data(data)

    def unpack_data(self, data):
        s = struct.Struct('<BB')
        (answer_order, error_code) = s.unpack(data[4:6])
        return answer_order, error_code


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

    dns = Dns_3000()
    camera = 502
    preset = 29
    print(dns.call_preset(camera, preset))
    print(dns.set_preset(camera, preset))
    print(dns.toggle_command(camera))
    print(dns.manual_control('pan', camera, 'left', 2))
    print(dns.received(b'\x04\x0A\x01\x00\x06\x00\x00\x00\x00\x09'))
