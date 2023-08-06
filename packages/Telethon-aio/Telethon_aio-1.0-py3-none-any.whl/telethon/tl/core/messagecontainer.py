import logging
import struct

from .tlmessage import TLMessage
from ..tlobject import TLObject

__log__ = logging.getLogger(__name__)


class MessageContainer(TLObject):
    CONSTRUCTOR_ID = 0x73f1f8dc

    def __init__(self, messages):
        self.messages = messages

    def to_dict(self):
        return {
            '_': 'MessageContainer',
            'messages':
                [] if self.messages is None else [
                    None if x is None else x.to_dict() for x in self.messages
                ],
        }

    def __bytes__(self):
        return struct.pack(
            '<Ii', MessageContainer.CONSTRUCTOR_ID, len(self.messages)
        ) + b''.join(bytes(m) for m in self.messages)

    @classmethod
    def from_reader(cls, reader):
        # This assumes that .read_* calls are done in the order they appear
        messages = []
        for _ in range(reader.read_int()):
            msg_id = reader.read_long()
            seq_no = reader.read_int()
            length = reader.read_int()
            before = reader.tell_position()
            obj = reader.tgread_object()
            messages.append(TLMessage(msg_id, seq_no, obj))
            if reader.tell_position() != before + length:
                reader.set_position(before)
                __log__.warning('Data left after TLObject {}: {!r}'
                                .format(obj, reader.read(length)))
        return MessageContainer(messages)
