# import time
#
# from binascii import unhexlify
#
# from Crypto.Cipher import AES
# from Crypto.Hash import CMAC
#
# MASTER_KEY = b'\xc3' * 16
# DK0_INTERVAL = 7200
# DK1_INTERVAL = 86400
#
#
# def set_master_key(key):
#     global MASTER_KEY
#     MASTER_KEY = unhexlify(key)
#
#
# class Beacon:
#     def __init__(self, b_id: bytes) -> None:
#         self.id = b_id
#         cmac = CMAC.new(MASTER_KEY, ciphermod=AES)
#         cmac.update(b_id)
#         self.key = cmac.digest()
#         self.dk = None  # type: int
#         self.clock = None  # type: int
#         self.clock_origin = None  # type: float
#         self.mask = 0
#
#     def validate_dk(self, new_dk: int, new_clock: int) -> bool:
#         if self.dk is None or self.clock is None:
#             self.dk = new_dk
#             self.clock = new_clock
#             return True
#         # Reset and calculate mask
#         for i in range(self.clock + 1, new_clock + 1):
#             if i % DK0_INTERVAL == 0:
#                 self.evolve_dk(0)
#             if i % DK1_INTERVAL == 0:
#                 self.evolve_dk(1)
#         self.clock = new_clock
#         # If the beacon has been out of sight long enough that we have
#         # no contemporary dk info
#         if self.mask == 0:
#             self.dk = new_dk
#             return True
#         # Compare the incoming dk masked with our known uncertainty to
#         # our generated value
#         if self.dk != (new_dk & self.mask):
#             # print(
#             #    """Failed DK:\n
#             #    \tLocal : {:032b}
#             #    \tBeacon: {:032b}
#             #    \tMask  : {:32b}""".format(self.dk, new_dk, self.mask))
#             return False
#         self.dk = new_dk
#         return True
#
#     def clock_skew(self, new_clock: int) -> float:
#         # Returns clock skew in seconds from expected clock time
#         if self.clock_origin is not None:
#             return time.time() - (self.clock_origin + new_clock)
#         else:
#             self.clock_origin = time.time() - new_clock
#             return 0.0
#
#     def evolve_dk(self, num: int) -> None:
#         # Evolve the DK. Same algo as the "beacon", but we know we'll
#         # be masking the unknown bits, so shift in zeros
#         high, low = self.dk >> 16, self.dk & 0x0000ffff
#         mask_high, mask_low = self.mask >> 16, self.mask & 0x0000ffff
#         if num == 0:
#             low = (low << 1) & 0xffff
#             mask_low = (mask_low << 1) & 0xffff
#         if num == 1:
#             high = (high << 1) & 0xffff
#             mask_high = (mask_high << 1) & 0xffff
#         self.dk = (high << 16) | (low & 0xffff)
#         self.mask = (mask_high << 16) | mask_low
