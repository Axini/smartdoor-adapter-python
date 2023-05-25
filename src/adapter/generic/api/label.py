from datetime import datetime
from enum import Enum
from typing import List

from generic.api import label_pb2
from generic.api.parameter import Parameter


class Sort(Enum):
    """
    Enumeration describing the Sort of message
    """
    STIMULUS = 0
    RESPONSE = 1


class Label:
    """
    DTO describing the Label message.
    Has convenient methods to en- and decode to Google Protobuf format
    """

    def __init__(self, sort: Sort, name: str, channel: str, parameters: List[Parameter] = None,
                 timestamp: datetime = None, physical_label: bytes = None, correlation_id: int = 0):
        parameters = parameters or []

        if not isinstance(sort, Sort):
            raise ValueError('sort should be of the enumeration Sort')

        if not name:
            raise ValueError('name should be filled in')

        if not channel:
            raise ValueError('channel should be filled in')

        if not parameters:
            self.parameters = []

        self.sort = sort
        self.name = name
        self.channel = channel
        self.parameters = parameters

        self.timestamp = timestamp
        self.physical_label = physical_label
        self.correlation_id = correlation_id

    def encode(self) -> label_pb2.Label:
        """
        Encode this object in Google Protobuf format

        Returns:
            label_pb2.Label: The label encoded in Google Protobuf format
        """
        pb_label = label_pb2.Label(
            label=self.name,
            type=self.sort.value,
            channel=self.channel,
            parameters=[param.encode() for param in self.parameters],
        )

        if self.timestamp:
            pb_label.timestamp = int(self.timestamp.timestamp() * 1e9)
        if self.physical_label:
            pb_label.physical_label = self.physical_label
        if self.correlation_id:
            pb_label.correlation_id = self.correlation_id

        return pb_label

    def __eq__(self, other):
        if isinstance(other, Label):
            return self.__dict__ == other.__dict__

    @classmethod
    def decode(cls, pb_label: label_pb2.Label):
        """
        Factory method for decoding from Google Protobuf format to this DTO

        Args:
            pb_label (label_pb2.Label)

        Returns:
            Label
        """
        timestamp = datetime.fromtimestamp(pb_label.timestamp / 1e6) \
            if pb_label.timestamp else datetime.now().timestamp()

        physical_label = pb_label.physical_label.decode('UTF-8') if pb_label.physical_label else None

        label = Label(name=pb_label.label,
                      channel=pb_label.channel,
                      sort=Sort(pb_label.type),
                      parameters=[Parameter.decode(pb_param) for pb_param in pb_label.parameters],
                      correlation_id=pb_label.correlation_id,
                      physical_label=physical_label,
                      timestamp=timestamp)

        return label
