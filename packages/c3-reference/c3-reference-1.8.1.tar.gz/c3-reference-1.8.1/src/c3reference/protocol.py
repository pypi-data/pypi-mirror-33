# import asyncio
# from math import sqrt
# import struct

# from binascii import hexlify
# import lzo
# from typing import Any
# from uuid import UUID

# from Crypto.Cipher import AES

# from .beacon import Beacon
# from .proto.common_pb2 import ListenerID
# from .proto.location_pb2 import IBeaconSummary


class PacketType:
    """Enum emulation class."""

    ID = 0
    DATA = 1
    SECURE = 2


# HEADER_LENGTH = 3
# BEACONS = {}  # type: Dict[bytes, Beacon]


def batt_2032_pct(mvolts):
    batt_pct = 0

    if mvolts >= 3000:
        batt_pct = 100
    elif mvolts > 2900:
        batt_pct = 100 - ((3000 - mvolts) * 58) / 100
    elif mvolts > 2740:
        batt_pct = 42 - ((2900 - mvolts) * 24) / 160
    elif mvolts > 2440:
        batt_pct = 18 - ((2740 - mvolts) * 12) / 300
    elif mvolts > 2100:
        batt_pct = 6 - ((2440 - mvolts) * 6) / 340
    return batt_pct


# class SecBeaconProtocol(object):
#     callback = None
#
#     def __init__(self):
#         self._rx_buf = bytearray()
#         self.transport = None
#         self.frame_remaining = None
#         self.flags = None
#
#     def connection_made(self,
#                         transport: Any) -> None:
#         self.transport = transport
#         self.peername = transport.get_extra_info('peername')[0]
#         print("{} has connected".format(self.peername))
#
#     def eof_received(self):
#         print("{} has disconnected".format(self.peername))
#
#     def data_received(self, data: bytes) -> None:
#         while len(data):
#             if not self.frame_remaining:
#                 # First byte of frame
#                 (self.frame_remaining,) = struct.unpack("!I", data[:4])
#                 self.flags = data[4]
#                 data = data[5:]
#             self._rx_buf.extend(data[:self.frame_remaining])
#             data = data[self.frame_remaining:]
#             self.frame_remaining -= max(len(data), self.frame_remaining)
#             if self.frame_remaining is 0:
#                 if self.flags >> 7:
#                     print("Compressed Len:", len(self._rx_buf))
#                     self._rx_buf = lzo.decompress(bytes(self._rx_buf), False,
#                                                   len(self._rx_buf)*4)
#                 p_type = self.flags & 0x7f
#                 asyncio.async(self.process_packet(self._rx_buf, p_type))
#                 self._rx_buf = bytearray()
#
#     async def process_packet(self, packet, p_type):
#         msg = {'peer': self.peername}
#         if p_type == PacketType.ID:
#             l_id = ListenerID()
#             l_id.ParseFromString(packet)
#             self.l_id = l_id.listener_id
#             print("Connected to {} ({}, {})".format(
#                 l_id.name, hexlify(
#                     l_id.listener_id).decode('utf-8'), l_id.version))
#             return
#         elif p_type == PacketType.DATA:
#             data = IBeaconSummary()
#             data.ParseFromString(packet)
#             print("\nIBeacon Report:")
#             print("\tClock:", data.clock)
#             for b in data.reports:
#                 print("\t{}/{}/{}".format(
#                     hexlify(b.uuid).decode(), b.major, b.minor))
#                 print("\t\tCount: {}".format(b.count))
#             return
#         elif p_type == PacketType.SECURE:
#             return
#         else:
#             return
#         # Header Parsing
#         msg = {"peer": self.peername}
#         msg["l_id"] = self.l_id.decode()
#         # Report Processing
#         data = packet[HEADER_LENGTH + l_id_len:]
#         if packet_type == PacketType.DATA:
#             msg["type"] = "ibeacon"
#             data_l = []
#             m_data = {}
#             m_data["num_reports"] = num_reports = len(data) // record_length
#             for idx in range(num_reports):
#                 m_data = {}
#                 rpt = data[idx * record_length:(idx + 1) * record_length]
#                 (uuid, m_data["major"], m_data["minor"], m_data["count"],
#                  distance_cm,
#                  variance_cm) = struct.unpack(
#                      "!16sHHHHH", rpt)
#                 m_data["distance"] = distance_cm / 100.0
#                 m_data["variance"] = variance_cm / 1000.0
#                 m_data["uuid"] = str(UUID(bytes=uuid))
#                 data_l.append(m_data)
#             msg["data"] = data_l
#
#         elif packet_type == PacketType.SECURE:
#             # if not len(data) == 39:
#             #     print(data)
#             #     return
#             (b_id, nonce, ciphertext, tag, distance,
#              variance) = struct.unpack("<6s 16s 9s 4s H H", data)
#             # BLE Mac comes across the line in reverse order. We
#             # reverse it for printing; but MAC calculations are on the
#             # raw value
#             m_data = {}
#             m_data["b_id"] = bytes(
#                 [b_id[i] for i in range(len(b_id) - 1, -1, -1)]).hex()
#             m_data["distance"] = distance / 100
#             m_data["variance"] = variance / 100
#             if b_id not in BEACONS:
#                 BEACONS[b_id] = Beacon(b_id)
#             beacon = BEACONS[b_id]
#             cipher = AES.new(beacon.key, AES.MODE_EAX, nonce, mac_len=4)
#             cipher.update(b_id)
#             try:
#                 plaintext = cipher.decrypt_and_verify(ciphertext, tag)
#             except ValueError as decrypt_verify_error:
#                 msg['type'] = "secbeacon_auth_failure"
#                 msg['data'] = str(decrypt_verify_error)
#                 if self.callback:
#                     await self.callback(msg)
#                 else:
#                     print(msg)
#                 return
#             (clock, dk, flags) = struct.unpack("<IIB", plaintext)
#             if beacon.clock and clock <= beacon.clock:
#                 if beacon.clock_skew(clock) > 2:
#                     # Reject old clock values
#                     msg["type"] = "secbeacon_replay_failure"
#                     msg["data"] = "Attempted replay of {}".format(clock)
#             dk_valid = beacon.validate_dk(dk, clock)
#             beacon.mask = 0xffffffff
#             msg["type"] = "secbeacon"
#             m_data["clock"] = clock
#             m_data["skew"] = beacon.clock_skew(clock)
#             m_data["button"] = flags & 0x1
#             batt_u = flags >> 1
#             batt_mv = batt_u * 28.125
#             m_data["battery_mv"] = round(batt_mv)
#             m_data["battery_pct"] = round(batt_2032_pct(batt_mv))
#             m_data["dk_valid"] = dk_valid
#             msg["data"] = m_data
#         elif packet_type == PacketType.KEEPALIVE:
#             msg["type"] = "listener_keepalive"
#             msg["data"] = hexlify(l_id)
#         else:
#             msg["type"] = "listener_error"
#             msg["data"] = "Unknown Packet type: {}".format(packet_type)
#         if self.callback:
#             await self.callback(msg)
#         else:
#             print(msg)
#         self.transport.write(b'ACK')
#
#     def error_received(self, exc: Exception) -> None:
#         print('Error received:', exc)
#
#     def connection_lost(self, exc: Exception) -> None:
#         print("{} has disconnected".format(self.peername))
