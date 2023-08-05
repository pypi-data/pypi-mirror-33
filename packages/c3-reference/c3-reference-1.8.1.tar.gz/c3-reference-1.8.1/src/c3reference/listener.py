#!/bin/env python
"""Simulates the traffic of one or more listeners or beacons."""
import time
import argparse
import asyncio
import os
import random
import struct

# from binascii import unhexlify
from enum import IntEnum

import lzo

# from Crypto.Cipher import AES
# from Crypto.Hash import CMAC

from .proto.common_pb2 import ListenerID
from .proto.location_pb2 import IBeaconSummary

# Configuration
DK0_INTERVAL = 7200
DK1_INTERVAL = 86400
PERCENT_DROPPED_PACKETS = 10
AVG_BEACON_DISTANCE = 3  # Meters

parser = argparse.ArgumentParser(
    description='Start a stub listener providing secbeacon packets')
parser.add_argument('--server', '-s', default="127.0.0.1",
                    help="Aggregator address")
parser.add_argument('--port', '-p', type=int, default=9999,
                    help="Aggregator port number")
parser.add_argument('--verbose', '-v', action='store_true',
                    help="Dump contents of each packet sent")
# parser.add_argument('--num-beacons', '-nb', type=int, default=0,
#                    help="Number of secure beacons to simulate")
parser.add_argument('--num-ibeacons', '-ib', type=int, default=10,
                    help="Number of non-secure ibeacons to simulate")
parser.add_argument('--num-listeners', '-nl', type=int, default=1,
                    help="Number of unique listeners to simulate")
parser.add_argument('--master-key', '-key', default=('c3' * 16),
                    help="Key from which to derive beacon keys")


class MessageType(IntEnum):
    ID = 0
    IBEACON = 1
    SECURE = 2
    RESPONSE = 3
    REQUEST = 4


def frame(protobuf_msg, msg_type=MessageType.IBEACON, compress=True):
    msg = protobuf_msg.SerializeToString()
    if compress:
        msg = lzo.compress(msg, 6, False)
    header = struct.pack("!IB", len(msg), (msg_type & 0x7f) | compress << 7)
    return header + msg


class IBeacon:
    def __init__(self, uuid: bytes = None, major: int = None,
                 minor: int = None) -> None:
        if not uuid:
            uuid = os.urandom(16)
        self.uuid = uuid

        if not major:
            major = random.randint(0, 2**16 - 1)
        self.major = major

        if not minor:
            minor = random.randint(0, 2**16 - 1)
        self.minor = minor

    def generate_report(self, report):
        report.uuid = self.uuid
        report.major_num = self.major
        report.minor_num = self.minor
        report.count = random.randint(0, 255)
        report.distance_cm = random.randint(0, AVG_BEACON_DISTANCE * 200)
        report.variance = random.randint(1, 20)
        report.reason = random.choice([report.ENTRY, report.EXIT, report.MOVE, report.STATUS])


class Listener:
    transport = None  # type: asyncio.DatagramTransport

    def __init__(self, num: int, l_id) -> None:
        self.l_id = l_id
        self.children = []  # type: list[IBeacon]
        family_uuid = os.urandom(6)
        family_major = random.randint(0, 2**16 - 1)
        for unused in range(num):
            self.children.append(IBeacon(family_uuid, family_major))

    async def task(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport
        await asyncio.sleep(random.random())
        while True:
            self.send_packet()
            await asyncio.sleep(random.randint(0, 5))

    def send_packet(self) -> None:
        summary = IBeaconSummary()
        summary.clock = int(time.time())
        random.shuffle(self.children)
        num_rpts = random.randint(0, len(self.children))
        if num_rpts == 0:
            return
        for b in self.children[:num_rpts]:
            rpt = summary.reports.add()
            b.generate_report(rpt)
        self.transport.write(frame(summary, MessageType.IBEACON, num_rpts > 1))


# class Beacon:
#     transport = None  # type: asyncio.DatagramTransport
#
#     def __init__(self, beacon_id: bytes = None) -> None:
#         if beacon_id is None:
#             self._id = bytes(
#                 [random.randint(0, 255) for i in range(6)])
#         else:
#             self._id = beacon_id
#         cmac = CMAC.new(unhexlify(args.master_key), ciphermod=AES)
#         cmac.update(self.id)
#         self.key = cmac.digest()
#         self.clock = random.randint(0, 2**10-1)
#         self.dk = random.randint(0, 2**32-1)
#         self.iterate()
#
#     @property
#     def id(self) -> bytes:
#         return self._id
#
#     async def task(self, transport: asyncio.DatagramTransport) -> None:
#         self.transport = transport
#         await asyncio.sleep(random.random())
#         while True:
#             # Update beacon state
#             self.iterate()
#             if random.randint(1, 100) > PERCENT_DROPPED_PACKETS:
#                 self.send_packet()
#             await asyncio.sleep(1)
#
#     def iterate(self) -> None:
#         self.clock += 1
#         if self.clock % DK0_INTERVAL == 0:
#             self.evolve_dk(0)
#         if self.clock % DK1_INTERVAL == 0:
#             self.evolve_dk(1)
#         self.nonce = os.urandom(16)
#         battery = 64 + (os.urandom(1)[0] >> 2)
#         button = random.choice([0,1])
#         self.flags = (battery << 1) | button
#
#     def dump(self, buf: bytes, l_id: bytes, payload: bytes,
#              tag: bytes, distance: float, variance: float) -> None:
#         print("""
# Packet: {0}
# \tListener ID: {1}
# \tBeacon ID: {2}
# \tNonce: {3}
# \tPayload: {4}
# \t\tClock: {5}
# \t\tDK: {6:08x}
# \t\tFlags: {7:02x}
# \tTag: {8}
# \tDistance: {9}m
# \tVariance: {10}""".format(buf.hex(), l_id.hex(), self.id.hex(),
#                            self.nonce.hex(), payload.hex(),
#                            self.clock, self.dk,
#                            self.flags,
#                            tag.hex(), (distance / 100.0), (variance / 100.0)))
#
#     def evolve_dk(self, num: int) -> None:
#         # Evolve the DK. Same algo as the "beacon", but we know we'll
#         # be masking the unknown bits, so shift in zeros
#         high, low = self.dk >> 16, self.dk & 0x0000ffff
#         if num == 0:
#             low = (low << 1) & 0xffff
#         if num == 1:
#             high = high << 1 & 0xffff
#         self.dk = (high << 16) | low & 0xffff
#
#     def send_packet(self) -> None:
#         # Generate Enciphered Payload and MAC tag
#         msg = struct.pack("<IIB", self.clock, self.dk, self.flags)
#         cipher = AES.new(self.key, AES.MODE_EAX, self.nonce,
#                          mac_len=4)
#         cipher.update(self.id)
#         ciphertext, tag = cipher.encrypt_and_digest(msg)
#         # Generate Header
#         buf = b'\x02'  # Version and Packet Type
#         msg_len = len(self.id + self.nonce + ciphertext + tag)
#         buf += struct.pack("B", msg_len)
#         l_id = random.choice(LISTENERS)
#         buf += struct.pack("B{}s".format(len(l_id)), len(l_id), l_id)
#         # Append Report
#         distance = random.randint(0, AVG_BEACON_DISTANCE * 200)
#         variance = random.randint(1, 20)
#         buf += struct.pack("<6s 16s 9s 4s H H", self.id, self.nonce,
#                            ciphertext, tag, distance, variance)
#         from binascii import hexlify
#         print("BUF", hexlify(struct.pack("<6s 16s 9s 4s H H", self.id, self.nonce,
#                                          ciphertext, tag, distance, variance)[-31:]))
#         if args.verbose:
#             self.dump(buf, l_id, ciphertext, tag, distance, variance)
#         print("BUF", buf)
#         self.transport.write(hdlc_frame(buf))


class ListenerProtocol:
    transport = None  # type: asyncio.DatagramTransport

    def eof_received(self):
        print('Authserver closed connection.')
        exit(0)

    def connection_made(self, transport):
        self.transport = transport
        l_id = ListenerID()
        l_id.name = "Fake Listener"
        l_id.listener_id = os.urandom(6)
        l_id.version = "v0.0.0-fake"
        transport.write(frame(l_id, MessageType.ID, False))
        loop = asyncio.get_event_loop()
        # for beacon in [Beacon() for i in range(args.num_beacons)]:
        #     loop.create_task(beacon.task(transport))
        listener = Listener(args.num_ibeacons // args.num_listeners, l_id.listener_id.hex())
        loop.create_task(listener.task(transport))

    def data_received(self, data: bytes):
        pass

    def error_received(self, exc: Exception) -> None:
        print('Error received:', exc)

    def connection_lost(self, exc: Exception) -> None:
        print('closing transport', exc)


# LISTENERS = [os.urandom(6) for i in range(args.num_listeners)]


async def _main(loop):
    global args
    args = parser.parse_args()
    random.seed(os.urandom(16))

    print("Simulating {} ibeacons spread across {} listener connections. Sending reports to {}:{}".format(
        args.num_ibeacons, args.num_listeners, args.server, args.port))

    loop = asyncio.get_event_loop()

    async def create_listener():
        try:
            return await loop.create_connection(ListenerProtocol, host=args.server, port=args.port)
        except Exception as e:
            print("Connection failed: {}".format(e))

    asyncio.gather(
        *[create_listener() for _ in range(args.num_listeners)], loop=loop)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit(0)
