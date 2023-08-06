import lzo
import struct

import attr
from automat import MethodicalMachine

HEADER_LEN = 5


@attr.s
class RawMessage(object):
    data = attr.ib()
    type = attr.ib()


class Frame(object):
    _data_len = None
    _machine = MethodicalMachine()

    def __init__(self):
        self._data_len = 0
        self._compressed_p = False
        self._header = bytearray()
        self._data = bytearray()
        self._message_type = -1
        self.msg_buf = []

    @_machine.input()
    def add_bytes(self, data):
        """ Client calls this method to add rx'd bytes to the frame. """

    @_machine.input()
    def _have_header(self):
        """The header is complete."""

    @_machine.input()
    def _have_data(self):
        """The data is complete."""

    @_machine.input()
    def _have_compressed_data(self):
        """The data is complete, but compressed."""

    @_machine.input()
    def bad_frame(self):
        """ The frame is invalid. """

    @staticmethod
    def _save(data, dest, dest_len):
        cur = len(dest)
        remaining = dest_len - cur
        if len(data) >= remaining:
            dest.extend(data[:remaining])
            return True, data[remaining:]
        dest.extend(data)
        return False, None

    @_machine.output()
    def _save_header(self, data):
        done, remaining = self._save(data, self._header, HEADER_LEN)
        if done:
            self._have_header()
            self.add_bytes(remaining)

    @_machine.output()
    def _process_header(self):
        (self._data_len, flags) = struct.unpack("!IB", self._header[:5])
        self._compressed_p = True if flags >> 7 else False
        self.message_type = flags & ~(1 << 7)

    @_machine.output()
    def _save_data(self, data):
        done, remaining = self._save(data, self._data, self._data_len)
        if done:
            if self._compressed_p:
                self._have_compressed_data()
            else:
                self._have_data()
            if remaining:
                self.add_bytes(remaining)

    @_machine.state(initial=True)
    def _waiting_for_header(self):
        """In this state we don't have the header"""

    @_machine.state()
    def _waiting_for_data(self):
        """In this state we don't have all the data"""

    @_machine.output()
    def _decompress_data(self):
        try:
            d = lzo.decompress(bytes(self._data), False, 10240)  # 10kiB max payload
            self._data = d
            self._have_data()
        except lzo.error as e:
            print("Bad compressed frame: {}".format(e))
            self.bad_frame()

    @_machine.output()
    def _process_message(self):
        self.msg_buf.append(RawMessage(bytes(self._data), self.message_type))

    @_machine.output()
    def _clear(self):
        self._data = bytearray()
        self._header = bytearray()

    def get_messages(self):
        r = self.msg_buf
        self.msg_buf = []
        return r

    _waiting_for_header.upon(add_bytes, enter=_waiting_for_header,
                             outputs=[_save_header])
    _waiting_for_header.upon(_have_header, enter=_waiting_for_data,
                             outputs=[_process_header])
    _waiting_for_data.upon(add_bytes, enter=_waiting_for_data,
                           outputs=[_save_data])
    _waiting_for_data.upon(_have_compressed_data, enter=_waiting_for_data,
                           outputs=[_decompress_data])
    _waiting_for_data.upon(_have_data, enter=_waiting_for_header,
                           outputs=[_process_message, _clear])
    _waiting_for_data.upon(bad_frame, enter=_waiting_for_header,
                           outputs=[_clear])


def frame_message(data, compress=False):
    from c3agg.listener import MessageType
    flags = (1 << 7) if compress else 0
    flags |= MessageType.REQUEST
    data = lzo.compress(data, 6, False) if compress else data
    header = struct.pack("!IB", len(data), flags)
    return b''.join([header, data])
