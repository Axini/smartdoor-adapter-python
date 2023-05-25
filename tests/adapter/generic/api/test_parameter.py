from datetime import datetime, date

import pytest as pytest

from adapter.generic.api import label_pb2
from adapter.generic.api.parameter import Parameter
from adapter.generic.api.type import Type
from adapter.generic.util.namespace_util import to_obj


def test_can_create_parameter():
    param = Parameter('some_param', Type.STRING, None)

    assert param
    assert param.name
    assert param.tipe
    assert not param.value


def test_param_must_have_a_name():
    with pytest.raises(ValueError):
        Parameter(None, Type.INTEGER, None)

    with pytest.raises(ValueError):
        Parameter('', Type.BOOLEAN, None)


def test_param_type_must_be_of_type_sort():
    with pytest.raises(ValueError):
        Parameter('a_param', None, None)

    with pytest.raises(ValueError):
        Parameter('a_param', 2, None)


def test_param_type_must_be_compatible_with_value():
    assert Parameter('a_param', Type.STRING, 'aaa')

    with pytest.raises(ValueError):
        Parameter('a_param', Type.STRING, 1)


def test_param_with_string_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.STRING, 'aaa').encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(string='aaa'))


def test_param_with_int_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.INTEGER, 1).encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(integer=1))


def test_param_with_bool_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.BOOLEAN, True).encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(boolean=True))


def test_param_with_decimal_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.DECIMAL, 1.1).encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(decimal=1.1))


def test_param_with_decimal_type_def_can_be_encoded():
    pb_param = Parameter('a_param', Type.DECIMAL).encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(decimal=1.0))


def test_param_with_time_type_can_be_encoded():
    timestamp = datetime(year=2023, month=4, day=24, hour=15, minute=19)
    pb_param = Parameter('a_param', Type.TIME, timestamp).encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(
        time=int(timestamp.timestamp() * 1e6)))


def test_param_with_date_type_can_be_encoded():
    datestamp = datetime(year=2023, month=4, day=24)
    pb_param = Parameter('a_param', Type.DATE, datestamp.date()).encode()

    assert pb_param == label_pb2.Label.Parameter(name='a_param', value=label_pb2.Label.Parameter.Value(
        date=int(datestamp.timestamp() * 1e3)))


def test_param_with_array_type_can_only_hold_elements_of_same_type():
    with pytest.raises(ValueError):
        Parameter('a_param', Type.ARRAY, [1, 'a']).encode()

def test_param_equality():
    assert Parameter('a_param', Type.ARRAY, [1, 2]) == Parameter('a_param', Type.ARRAY, [1, 2])

def test_param_with_array_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.ARRAY, [1, 2]).encode()

    assert pb_param == label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(
            array=label_pb2.Label.Parameter.Value.Array(
                values=[label_pb2.Label.Parameter.Value(integer=1), label_pb2.Label.Parameter.Value(integer=2)]
            )
        )
    )


def test_param_with_array_type_def_can_be_encoded():
    pb_param = Parameter('a_param', Type.ARRAY, [Type.STRING]).encode()

    assert pb_param == label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(
            array=label_pb2.Label.Parameter.Value.Array(
                values=[label_pb2.Label.Parameter.Value(string='string')]
            )
        )
    )


def test_param_with_struct_type_def_can_be_encoded():
    pb_param = Parameter('a_param', Type.STRUCT, to_obj({"a_key": Type.STRING, "another_key": Type.INTEGER})).encode()

    assert pb_param == label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(
            struct=label_pb2.Label.Parameter.Value.Hash(
                entries=[label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='a_key'),
                    value=label_pb2.Label.Parameter.Value(string='string')
                ), label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='another_key'),
                    value=label_pb2.Label.Parameter.Value(integer=1)
                )
                ]
            )
        )
    )


def test_param_with_struct_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.STRUCT, to_obj({"a_key": 'a', "another_key": 2})).encode()

    assert pb_param == label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(
            struct=label_pb2.Label.Parameter.Value.Hash(
                entries=[label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='a_key'),
                    value=label_pb2.Label.Parameter.Value(string='a')
                ), label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='another_key'),
                    value=label_pb2.Label.Parameter.Value(integer=2)
                )
                ]
            )
        )
    )


def test_param_with_hash_type_def_can_be_encoded():
    pb_param = Parameter('a_param', Type.HASH, {Type.STRING: Type.STRING}).encode()

    assert pb_param == label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(
            hash_value=label_pb2.Label.Parameter.Value.Hash(
                entries=[label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='string'),
                    value=label_pb2.Label.Parameter.Value(string='string')
                )
                ]
            )
        )
    )


def test_param_with_hash_type_can_be_encoded():
    pb_param = Parameter('a_param', Type.HASH, {'some_key': 1, 'some_other_key': 2}).encode()

    assert pb_param == label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(
            hash_value=label_pb2.Label.Parameter.Value.Hash(
                entries=[label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='some_key'),
                    value=label_pb2.Label.Parameter.Value(integer=1)
                ), label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='some_other_key'),
                    value=label_pb2.Label.Parameter.Value(integer=2)
                )
                ]
            )
        )
    )


def test_encoding_param_with_hash_with_different_value_types_should_fail():
    with pytest.raises(ValueError):
        Parameter('a_param', Type.HASH, {'a': 'string', 'b': 1}).encode()


def test_encoding_and_decoding_is_symmetric():
    int_param = Parameter('int_param', Type.INTEGER, 3)
    assert Parameter.decode(int_param.encode()) == int_param


def test_param_with_integer_value_can_be_decoded():
    pb_param = label_pb2.Label.Parameter(
        name='a_param',
        value=label_pb2.Label.Parameter.Value(integer=2)
    )

    assert Parameter.decode(pb_param) == Parameter('a_param', Type.INTEGER, 2)


def test_param_with_string_value_can_be_encoded():
    pb_param = label_pb2.Label.Parameter(
        name='string_param',
        value=label_pb2.Label.Parameter.Value(string='some_string')
    )

    assert Parameter.decode(pb_param) == Parameter('string_param', Type.STRING, 'some_string')


def test_param_with_decimal_value_can_be_encoded():
    pb_param = label_pb2.Label.Parameter(
        name='dec_param',
        value=label_pb2.Label.Parameter.Value(decimal=1.2)
    )

    assert Parameter.decode(pb_param) == Parameter('dec_param', Type.DECIMAL, 1.2)


def test_param_with_boolean_value_can_be_encoded():
    pb_param = label_pb2.Label.Parameter(
        name='bool_param',
        value=label_pb2.Label.Parameter.Value(boolean=False)
    )

    assert Parameter.decode(pb_param) == Parameter('bool_param', Type.BOOLEAN, False)


def test_pb_param_with_date_value_can_be_decoded():
    pb_param = label_pb2.Label.Parameter(
        name='date_param',
        value=label_pb2.Label.Parameter.Value(
            date=int(datetime(year=2023, month=5, day=1).timestamp() * 1e3)
        )
    )

    assert Parameter.decode(pb_param) == Parameter('date_param', Type.DATE, date(year=2023, month=5, day=1))


def test_pb_param_with_time_value_can_be_decoded():
    pb_param = label_pb2.Label.Parameter(
        name='time_param',
        value=label_pb2.Label.Parameter.Value(
            time=int(
                datetime(year=2023, month=5, day=1, hour=15, minute=1, second=31, microsecond=23).timestamp() * 1e6)
        )
    )

    assert Parameter.decode(pb_param) == Parameter('time_param', Type.TIME, datetime(
        year=2023, month=5, day=1, hour=15, minute=1, second=31, microsecond=23))


def test_pb_param_with_array_can_be_decoded():
    pb_param = label_pb2.Label.Parameter(
        name='array_param',
        value=label_pb2.Label.Parameter.Value(
            array=label_pb2.Label.Parameter.Value.Array(
                values=[label_pb2.Label.Parameter.Value(string='a'), label_pb2.Label.Parameter.Value(string='b')]
            )
        )
    )

    assert Parameter.decode(pb_param) == Parameter('array_param', Type.ARRAY, ['a', 'b'])


def test_pb_param_with_struct_can_be_decoded():
    pb_param = label_pb2.Label.Parameter(
        name='struct_param',
        value=label_pb2.Label.Parameter.Value(
            struct=label_pb2.Label.Parameter.Value.Hash(
                entries=[label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='a_key'),
                    value=label_pb2.Label.Parameter.Value(string='a')
                ), label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='another_key'),
                    value=label_pb2.Label.Parameter.Value(integer=2)
                )
                ]
            )
        )
    )

    assert Parameter.decode(pb_param) == \
           Parameter('struct_param', Type.STRUCT, to_obj({'a_key': 'a', 'another_key': 2}))


def test_pb_param_with_hash_can_be_decoded():
    pb_param = label_pb2.Label.Parameter(
        name='hash_param',
        value=label_pb2.Label.Parameter.Value(
            hash_value=label_pb2.Label.Parameter.Value.Hash(
                entries=[label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='first_key'),
                    value=label_pb2.Label.Parameter.Value(string='a')
                ), label_pb2.Label.Parameter.Value.Hash.Entry(
                    key=label_pb2.Label.Parameter.Value(string='second_key'),
                    value=label_pb2.Label.Parameter.Value(string='b')
                )
                ]
            )
        )
    )

    assert Parameter.decode(pb_param) == \
           Parameter('hash_param', Type.HASH, {'first_key': 'a', 'second_key': 'b'})
