# A CAN message.

import binascii
from copy import deepcopy

from ..utils import format_or
from ..utils import start_bit
from ..utils import encode_data
from ..utils import decode_data
from ..utils import create_encode_decode_formats
from ..errors import Error


class EncodeError(Error):
    pass


class DecodeError(Error):
    pass


class Message(object):
    """A CAN message with frame id, comment, signals and other
    information.

    If `strict` is ``True`` an exception is raised if any signals are
    overlapping or if they don't fit in the message.

    """

    def __init__(self,
                 frame_id,
                 name,
                 length,
                 signals,
                 comment=None,
                 senders=None,
                 send_type=None,
                 cycle_time=None,
                 dbc_specifics=None,
                 is_extended_frame=False,
                 bus_name=None,
                 strict=True):
        self._frame_id = frame_id
        self._is_extended_frame = is_extended_frame
        self._name = name
        self._length = length
        self._signals = signals
        self._signals.sort(key=start_bit)
        self._comment = comment
        self._senders = senders if senders else []
        self._send_type = send_type
        self._cycle_time = cycle_time
        self._dbc = dbc_specifics
        self._bus_name = bus_name
        self._codecs = None
        self._signal_tree = None
        self._strict = strict
        self.refresh()

    def _create_codec(self, parent_signal=None, multiplexer_id=None):
        """Create a codec of all signals with given parent signal. This is a
        recursive function.

        """

        signals = []
        multiplexers = {}

        # Find all signals matching given parent signal name and given
        # multiplexer id. Root signals' parent and multiplexer id are
        # both None.
        for signal in self._signals:
            if signal.multiplexer_signal != parent_signal:
                continue

            if ((multiplexer_id is not None)
                and (multiplexer_id not in signal.multiplexer_ids)):
                continue

            if signal.is_multiplexer:
                children_ids = set()

                for s in self._signals:
                    if s.multiplexer_signal != signal.name:
                        continue

                    children_ids.update(s.multiplexer_ids)

                # Some CAN messages will have muxes containing only
                # the multiplexer and no additional signals. At Tesla
                # these are indicated in advance by assigning them an
                # enumeration. Here we ensure that any named
                # multiplexer is included, even if it has no child
                # signals.
                if signal.choices:
                    children_ids.update(signal.choices.keys())

                for child_id in children_ids:
                    codec = self._create_codec(signal.name, child_id)

                    if signal.name not in multiplexers:
                        multiplexers[signal.name] = {}

                    multiplexers[signal.name][child_id] = codec

            signals.append(signal)

        return {
            'signals': signals,
            'formats': create_encode_decode_formats(signals,
                                                    self._length),
            'multiplexers': multiplexers
        }

    def _create_signal_tree(self, codec):
        """Create a multiplexing tree node of given codec. This is a recursive
        function.

        """

        nodes = []

        for signal in codec['signals']:
            multiplexers = codec['multiplexers']

            if signal.name in multiplexers:
                node = {
                    signal.name: {
                        mux: self._create_signal_tree(mux_codec)
                        for mux, mux_codec in multiplexers[signal.name].items()
                    }
                }
            else:
                node = signal.name

            nodes.append(node)

        return nodes

    @property
    def frame_id(self):
        """The message frame id.

        """

        return self._frame_id

    @frame_id.setter
    def frame_id(self, value):
        self._frame_id = value

    @property
    def is_extended_frame(self):
        """``True`` if the message is an extended frame, ``False`` otherwise.

        """

        return self._is_extended_frame

    @is_extended_frame.setter
    def is_extended_frame(self, value):
        self._is_extended_frame = value

    @property
    def name(self):
        """The message name as a string.

        """

        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def length(self):
        """The message data length in bytes.

        """

        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    @property
    def signals(self):
        """A list of all signals in the message.

        """

        return self._signals

    @property
    def comment(self):
        """The message comment, or ``None`` if unavailable.

        """

        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value

    @property
    def senders(self):
        """A list of all sender nodes of this message.

        """

        return self._senders

    @property
    def send_type(self):
        """The message send type, or ``None`` if unavailable.

        """

        return self._send_type

    @property
    def cycle_time(self):
        """The message cycle time, or ``None`` if unavailable.

        """

        return self._cycle_time

    @property
    def dbc(self):
        """An object containing dbc specific properties like e.g. attributes.

        """

        return self._dbc

    @property
    def bus_name(self):
        """The message bus name, or ``None`` if unavailable.

        """

        return self._bus_name

    @bus_name.setter
    def bus_name(self, value):
        self._bus_name = value

    @property
    def signal_tree(self):
        """All signal names and multiplexer ids as a tree. Multiplexer signals
        are dictionaries, while other signals are strings.

        >>> foo = db.get_message_by_name('Foo')
        >>> foo.signal_tree
        ['Bar', 'Fum']
        >>> bar = db.get_message_by_name('Bar')
        >>> bar.signal_tree
        [{'A': {0: ['C', 'D'], 1: ['E']}}, 'B']

        """

        return self._signal_tree

    def _get_mux_number(self, decoded, signal_name):
        mux = decoded[signal_name]

        if isinstance(mux, str):
            signal = self.get_signal_by_name(signal_name)
            mux = signal.choice_string_to_number(mux)

        return mux

    def _encode(self, node, data, scaling):
        encoded = encode_data(data,
                              node['signals'],
                              node['formats'],
                              scaling)
        padding_mask = node['formats'].padding_mask
        multiplexers = node['multiplexers']

        for signal in multiplexers:
            mux = self._get_mux_number(data, signal)

            try:
                node = multiplexers[signal][mux]
            except KeyError:
                raise EncodeError('expected multiplexer id {}, but got {}'.format(
                    format_or(multiplexers[signal]),
                    mux))

            mux_encoded, mux_padding_mask = self._encode(node, data, scaling)
            encoded |= mux_encoded
            padding_mask &= mux_padding_mask

        return encoded, padding_mask

    def encode(self, data, scaling=True, padding=False):
        """Encode given data as a message of this type.

        If `scaling` is ``False`` no scaling of signals is performed.

        If `padding` is ``True`` unused bits are encoded as 1.

        >>> foo = db.get_message_by_name('Foo')
        >>> foo.encode({'Bar': 1, 'Fum': 5.0})
        b'\\x01\\x45\\x23\\x00\\x11'

        """

        encoded, padding_mask = self._encode(self._codecs, data, scaling)

        if padding:
            encoded |= padding_mask

        encoded |= (0x80 << (8 * self._length))
        encoded = hex(encoded)[4:].rstrip('L')

        return binascii.unhexlify(encoded)[:self._length]

    def _decode(self, node, data, decode_choices, scaling):
        decoded = decode_data(data,
                              node['signals'],
                              node['formats'],
                              decode_choices,
                              scaling)

        multiplexers = node['multiplexers']

        for signal in multiplexers:
            mux = self._get_mux_number(decoded, signal)

            try:
                node = multiplexers[signal][mux]
            except KeyError:
                raise DecodeError('expected multiplexer id {}, but got {}'.format(
                    format_or(multiplexers[signal]),
                    mux))

            decoded.update(self._decode(node,
                                        data,
                                        decode_choices,
                                        scaling))

        return decoded

    def decode(self, data, decode_choices=True, scaling=True):
        """Decode given data as a message of this type.

        If `decode_choices` is ``False`` scaled values are not
        converted to choice strings (if available).

        If `scaling` is ``False`` no scaling of signals is performed.

        >>> foo = db.get_message_by_name('Foo')
        >>> foo.decode(b'\\x01\\x45\\x23\\x00\\x11')
        {'Bar': 1, 'Fum': 5.0}

        """

        data = data[:self._length]

        return self._decode(self._codecs, data, decode_choices, scaling)

    def get_signal_by_name(self, name):
        for signal in self._signals:
            if signal.name == name:
                return signal

        raise KeyError(name)

    def is_multiplexed(self):
        """Returns ``True`` if the message is multiplexed, otherwise
        ``False``.

        >>> foo = db.get_message_by_name('Foo')
        >>> foo.is_multiplexed()
        False
        >>> bar = db.get_message_by_name('Bar')
        >>> bar.is_multiplexed()
        True

        """

        return bool(self._codecs['multiplexers'])

    @property
    def layout(self):
        """ASCII art of the message layout. Each signal is an arrow from LSB
        ``x`` to MSB ``<``. Overlapping signal bits are set to ``X``.

        .. code:: text

                                Bit

                   7   6   5   4   3   2   1   0
                 +---+---+---+---+---+---+---+---+
               0 |   |   |   |   |   |<----------|
                 +---+---+---+---+---+---+---+---+
               1 |------x|   |   |   |   |<-x|   |
                 +---+---+---+---+---+---+---+---+
               2 |   |   |   |   |   |   |   |   |
           B     +---+---+---+---+---+---+---+---+
           y   3 |----XXXXXXX---x|   |   |   |   |
           t     +---+---+---+---+---+---+---+---+
           e   4 |-------------------------------|
                 +---+---+---+---+---+---+---+---+
               5 |   |   |<----------------------|
                 +---+---+---+---+---+---+---+---+
               6 |   |   |   |   |   |   |   |   |
                 +---+---+---+---+---+---+---+---+
               7 |   |   |   |   |   |   |   |   |
                 +---+---+---+---+---+---+---+---+

        """

        def format_big():
            signals = []

            for signal in self._signals:
                if signal.byte_order != 'big_endian':
                    continue

                formatted = start_bit(signal) * '   '
                formatted += '<{}x'.format((3 * signal.length - 2) * '-')
                signals.append(formatted)

            return signals

        def format_little():
            signals = []

            for signal in self._signals:
                if signal.byte_order != 'little_endian':
                    continue

                formatted = signal.start * '   '
                formatted += 'x{}<'.format((3 * signal.length - 2) * '-')
                end = signal.start + signal.length

                if end % 8 != 0:
                    formatted += (8 - (end % 8)) * '   '

                formatted = ''.join([
                    formatted[i:i + 24][::-1]
                    for i in range(0, len(formatted), 24)
                ])
                signals.append(formatted)

            return signals

        def format_byte_lines():
            signals = format_big() + format_little()

            if len(signals) > 0:
                length = max([len(signal) for signal in signals])

                if length % 24 != 0:
                    length += (24 - (length % 24))

                signals = [signal + (length - len(signal)) * ' ' for signal in signals]

            formatted = ''

            for chars in zip(*signals):
                left = chars.count('<')
                dash = chars.count('-')
                x = chars.count('x')

                if left + dash + x > 1:
                    formatted += 'X'
                elif left == 1:
                    formatted += '<'
                elif dash == 1:
                    formatted += '-'
                elif x == 1:
                    formatted += 'x'
                else:
                    formatted += ' '

            byte_lines = [
                formatted[i:i + 24]
                for i in range(0, len(formatted), 24)
            ]

            unused_byte_lines = self._length - len(byte_lines)

            if unused_byte_lines > 0:
                byte_lines += unused_byte_lines * [24 * ' ']

            lines = []

            for byte_line in byte_lines:
                line = ''
                prev_byte = None

                for i in range(0, 24, 3):
                    byte_triple = byte_line[i:i + 3]

                    if i == 0:
                        line += '|' + byte_triple
                    elif byte_line[i] in ' <>x':
                        line += '|' + byte_triple
                    elif byte_line[i] == 'X':
                        if prev_byte == 'X':
                            line += 'X' + byte_triple
                        elif prev_byte == '-':
                            line += '-' + byte_triple
                        else:
                            line += '|' + byte_triple
                    else:
                        line += '-' + byte_triple

                    prev_byte = byte_line[i + 2]

                line += '|'
                lines.append(line)

            return lines

        def add_horizontal_and_header_lines(byte_lines):
            lines = [
                '               Bit',
                '',
                '  7   6   5   4   3   2   1   0',
                '+---+---+---+---+---+---+---+---+'
            ]

            for byte_line in byte_lines:
                lines.append(byte_line)
                lines.append('+---+---+---+---+---+---+---+---+')

            return lines

        def add_byte_numbers(lines):
            width = len(str((len(lines) - 4) // 2)) + 4
            fmt = '{{:{}d}} '.format(width - 1)
            numbers_lines = []

            for index in range(len(lines)):
                if index < 3 or (index % 2) == 1:
                    prefix = width * ' '
                else:
                    prefix = fmt.format((index - 4) // 2)

                numbers_lines.append(prefix)

            return [
                number_line + line
                for number_line, line in zip(numbers_lines, lines)
            ]

        def add_y_axis_name(lines):
            number_of_matrix_lines = (len(lines) - 3)
            start_index = 4

            if number_of_matrix_lines >= 4:
                start_index += (number_of_matrix_lines - 4) // 2 - 1

                if start_index < 4:
                    start_index = 4

            if len(lines) < 8:
                lines += (8 - len(lines)) * ['     ']

            axis_lines = []

            for index in range(len(lines)):
                if index == start_index:
                    prefix = ' B'
                elif index == start_index + 1:
                    prefix = ' y'
                elif index == start_index + 2:
                    prefix = ' t'
                elif index == start_index + 3:
                    prefix = ' e'
                else:
                    prefix = '  '

                axis_lines.append(prefix)

            return [
                axis_line + line
                for axis_line, line in zip(axis_lines, lines)
            ]

        lines = format_byte_lines()
        lines = add_horizontal_and_header_lines(lines)
        lines = add_byte_numbers(lines)
        lines = add_y_axis_name(lines)
        lines = [line.rstrip() for line in lines]

        return '\n'.join(lines)

    def _check_signal(self, message_bits, signal):
        signal_bits = signal.length * [signal.name]

        if signal.byte_order == 'big_endian':
            padding = start_bit(signal) * [None]
            signal_bits = padding + signal_bits
        else:
            signal_bits += signal.start * [None]

            if len(signal_bits) < len(message_bits):
                padding = (len(message_bits) - len(signal_bits)) * [None]
                reversed_signal_bits = padding + signal_bits
            else:
                reversed_signal_bits = signal_bits

            signal_bits = []

            for i in range(0, len(reversed_signal_bits), 8):
                signal_bits = reversed_signal_bits[i:i + 8] + signal_bits

        # Check that the signal fits in the message.
        if len(signal_bits) > len(message_bits):
            raise Error(
                'The signal {} does not fit in message {}.'.format(
                    signal.name,
                    self.name))

        # Check that the signal does not overlap with other
        # signals.
        for offset, signal_bit in enumerate(signal_bits):
            if signal_bit is not None:
                if message_bits[offset] is not None:
                    raise Error(
                        'The signals {} and {} are overlapping in message {}.'.format(
                            signal.name,
                            message_bits[offset],
                            self.name))

                message_bits[offset] = signal.name

    def _check_mux(self, message_bits, mux):
        signal_name, children = list(mux.items())[0]
        self._check_signal(message_bits,
                           self.get_signal_by_name(signal_name))
        children_message_bits = deepcopy(message_bits)

        for multiplexer_id in sorted(children):
            child_tree = children[multiplexer_id]
            child_message_bits = deepcopy(children_message_bits)
            self._check_signal_tree(child_message_bits, child_tree)

            for i, child_bit in enumerate(child_message_bits):
                if child_bit is not None:
                    message_bits[i] = child_bit

    def _check_signal_tree(self, message_bits, signal_tree):
        for signal_name in signal_tree:
            if isinstance(signal_name, dict):
                self._check_mux(message_bits, signal_name)
            else:
                self._check_signal(message_bits,
                                   self.get_signal_by_name(signal_name))

    def refresh(self, strict=None):
        """Refresh the internal message state.

        If `strict` is ``True`` an exception is raised if any signals
        are overlapping or if they don't fit in the message. This
        argument overrides the value of the same argument passed to
        the constructor.

        """

        self._codecs = self._create_codec()
        self._signal_tree = self._create_signal_tree(self._codecs)

        if strict is None:
            strict = self._strict

        if strict:
            message_bits = 8 * self.length * [None]
            self._check_signal_tree(message_bits, self.signal_tree)

    def __repr__(self):
        return "message('{}', 0x{:x}, {}, {}, {})".format(
            self._name,
            self._frame_id,
            self._is_extended_frame,
            self._length,
            "'" + self._comment + "'" if self._comment is not None else None)
