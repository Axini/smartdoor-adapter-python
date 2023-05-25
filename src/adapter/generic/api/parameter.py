from datetime import datetime, date
from types import SimpleNamespace
from typing import Any

from generic.api import label_pb2
from generic.api.type import Type
from generic.util.namespace_util import to_obj


def _determine_type_from_value(value) -> Type:
    tipe = None

    if type(value) == Type:
        tipe = value
    elif type(value) == dict:
        tipe = Type.HASH
    elif type(value) == SimpleNamespace:
        tipe = Type.STRUCT
    elif type(value) == list:
        tipe = Type.ARRAY
    elif type(value) == int:
        tipe = Type.INTEGER
    elif type(value) == date:
        tipe = Type.DATE
    elif type(value) == datetime:
        tipe = Type.TIME
    elif type(value) == float:
        tipe = Type.DECIMAL
    elif type(value) == str:
        tipe = Type.STRING
    elif type(value) == bool:
        tipe = Type.BOOLEAN

    return tipe


def _is_array_of_same_type(value) -> bool:
    # Value should be of type list, this is checked earlier, so we do not check this here
    return len(set(map(lambda val: type(val), value))) == 1


def _encode_value(tipe, value=None):
    if value and type(value) is Type:
        value = None

    if tipe == Type.STRING:
        value = 'string' if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(string=value)
    elif tipe == Type.INTEGER:
        value = 1 if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(integer=value)
    elif tipe == Type.BOOLEAN:
        value = True if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(boolean=value)
    elif tipe == Type.DECIMAL:
        value = 1.0 if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(decimal=value)
    elif tipe == Type.TIME:
        value = datetime.now() if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(time=int(value.timestamp() * 1e6))
    elif tipe == Type.DATE:
        value = date.today() if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(
            date=int(datetime(year=value.year, month=value.month, day=value.day).timestamp() * 1e3))
    elif tipe == Type.ARRAY:
        value = [] if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(array=_encode_array_value(value))
    elif tipe == Type.STRUCT:
        value = to_obj({}) if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(struct=_encode_hash_or_struct_entries(value.__dict__))
    elif tipe == Type.HASH:
        value = {} if value is None else value
        pb_value = label_pb2.Label.Parameter.Value(hash_value=_encode_hash_or_struct_entries(value))
    elif not tipe:
        pb_value = None
    else:
        raise ValueError('Can not encode parameter of type {tipe}'.format(tipe=tipe))

    return pb_value


def _encode_array_value(values):
    pb_values = [_encode_value(_determine_type_from_value(e), e) for e in values]
    return label_pb2.Label.Parameter.Value.Array(values=pb_values)


def _encode_hash_or_struct_entries(entries):
    def _encode_hash_or_struct_entry(key, val):
        return label_pb2.Label.Parameter.Value.Hash.Entry(
            key=_encode_value(_determine_type_from_value(key), key),
            value=_encode_value(_determine_type_from_value(val), val)
        )

    pb_entries = [_encode_hash_or_struct_entry(k, v) for k, v in entries.items()]
    return label_pb2.Label.Parameter.Value.Hash(entries=pb_entries)


def _decode_type_of_value(pb_value) -> Type:
    if pb_value.HasField('string'):
        return Type.STRING
    elif pb_value.HasField('integer'):
        return Type.INTEGER
    elif pb_value.HasField('decimal'):
        return Type.DECIMAL
    elif pb_value.HasField('boolean'):
        return Type.BOOLEAN
    elif pb_value.HasField('date'):
        return Type.DATE
    elif pb_value.HasField('time'):
        return Type.TIME
    elif pb_value.HasField('array'):
        return Type.ARRAY
    elif pb_value.HasField('struct'):
        return Type.STRUCT
    elif pb_value.HasField('hash_value'):
        return Type.HASH


def _decode_value(pb_value) -> Any:
    tipe = _decode_type_of_value(pb_value)
    val = None

    if tipe == Type.STRING:
        val = pb_value.string
    elif tipe == Type.INTEGER:
        val = pb_value.integer
    elif tipe == Type.DECIMAL:
        val = pb_value.decimal
    elif tipe == Type.BOOLEAN:
        val = pb_value.boolean
    elif tipe == Type.DATE:
        val = datetime.fromtimestamp(pb_value.date / 1e3).date()
    elif tipe == Type.TIME:
        val = datetime.fromtimestamp(pb_value.time / 1e6)
    elif tipe == Type.ARRAY:
        val = _decode_array(pb_value.array)
    elif tipe == Type.STRUCT:
        val = _decode_struct(pb_value.struct)
    elif tipe == Type.HASH:
        val = _decode_hash(pb_value.hash_value)

    return val


def _decode_array(pb_array):
    if len({_decode_type_of_value(pb_elem) for pb_elem in pb_array.values}) > 1:
        raise 'Array can only hold elements of a single type'

    return [_decode_value(pb_elem) for pb_elem in pb_array.values]


def _decode_struct(pb_struct):
    return to_obj({_decode_value(pb_elem.key): _decode_value(pb_elem.value) for pb_elem in pb_struct.entries})


def _decode_hash(pb_hash):
    if len({_decode_type_of_value(pb_elem.value) for pb_elem in pb_hash.entries}) > 1:
        raise 'Hashes can only hold elements of a single type'

    return {_decode_value(pb_elem.key): _decode_value(pb_elem.value) for pb_elem in pb_hash.entries}


class Parameter:
    """
    Data Transfer Object of a Parameter. Has convenient functions for en- and decoding to a Google Protobuf format.

    Attributes:
        name (string): Name of the parameter
        tipe (Type): Type of the parameter
        value (int|float|bool|date|datetime|List|dict|SimpleNamespace): Value of the parameter.
            Can be of different types. Defaults to None.
    """
    def __init__(self, name, tipe, value=None):
        if not name:
            raise ValueError('name must not be empty')

        if not isinstance(tipe, Type):
            raise ValueError('tipe must be of enum Type')

        if value and tipe != _determine_type_from_value(value):
            raise ValueError("value must be of same type as the given 'tipe'")

        if tipe == Type.ARRAY and not _is_array_of_same_type(value):
            raise ValueError("All elements in the array must be of the same type")

        if tipe == Type.HASH and not _is_array_of_same_type(value.values()):
            raise ValueError("All values in an hash must be of the same type")

        self.name = name
        self.tipe = tipe
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Parameter):
            return self.__dict__ == other.__dict__

    @classmethod
    def decode(cls, pb_param: label_pb2.Label.Parameter):
        """
        Factory method to decode a parameter in Google Protobuf format to this DTO

        Args:
            pb_param (label_pb2.Label.Parameter): parameter in Google Protobuf format

        Returns:
            Parameter: Instance of this DTO
        """
        tipe = _decode_type_of_value(pb_param.value)
        value = _decode_value(pb_param.value)

        return Parameter(pb_param.name, tipe, value=value)

    def encode(self) -> label_pb2.Label.Parameter:
        """
        Encode this DTO to Google Protobuf format.

        Returns:
            label_pb2.Label.Parameter: Parameter in Google Protobuf Format
        """
        return label_pb2.Label.Parameter(name=self.name, value=_encode_value(self.tipe, self.value))
