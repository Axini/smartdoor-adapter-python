from datetime import datetime

import pytest

from adapter.generic.api import label_pb2
from adapter.generic.api.label import Label, Sort
from adapter.generic.api.parameter import Parameter
from adapter.generic.api.type import Type


def test_can_create_a_label():
    label = Label(Sort.RESPONSE, 'some_label', 'some_channel', None)

    assert label
    assert label.sort == Sort.RESPONSE
    assert label.name == 'some_label'
    assert label.channel == 'some_channel'
    assert not label.parameters


def test_can_create_label_with_parameter_definitions():
    label = Label(Sort.STIMULUS, 'some_label2', 'another_channel', [Parameter('param1', Type.STRING)])

    assert label
    assert label.sort == Sort.STIMULUS
    assert label.name == 'some_label2'
    assert label.channel == 'another_channel'
    assert label.parameters
    assert label.parameters[0].name == 'param1'


def test_label_has_to_have_a_name():
    with pytest.raises(ValueError):
        Label(Sort.RESPONSE, None, 'some_channel', None)

    with pytest.raises(ValueError):
        Label(Sort.STIMULUS, '', 'some_channel', None)


def test_label_has_to_have_a_channel():
    with pytest.raises(ValueError):
        Label(Sort.RESPONSE, 'some_label', None, [])

    with pytest.raises(ValueError):
        Label(Sort.STIMULUS, 'some_label', '', [])


def test_label_definitions_can_be_encoded():
    label = Label(Sort.RESPONSE, 'some_label', 'some_channel', [Parameter('param1', Type.INTEGER)])

    assert label.encode() == label_pb2.Label(
        label='some_label',
        type=Sort.RESPONSE.value,
        channel='some_channel',
        parameters=[label_pb2.Label.Parameter(name='param1', value=label_pb2.Label.Parameter.Value(integer=1))]
    )


def test_label_can_be_encoded():
    ts = datetime.now()

    label = Label(Sort.STIMULUS, 'some_label', 'some_channel', [Parameter('param1', Type.INTEGER, 2)],
                  correlation_id=1000,
                  timestamp=ts
                  )

    assert label.encode() == label_pb2.Label(
        label='some_label',
        type=Sort.STIMULUS.value,
        channel='some_channel',
        parameters=[label_pb2.Label.Parameter(name='param1', value=label_pb2.Label.Parameter.Value(integer=2))],
        correlation_id=1000,
        timestamp=int(ts.timestamp() * 1e9)
    )


def test_label_can_be_decoded():
    ts = datetime.now()

    pb_label = label_pb2.Label(
        label='some_other_label',
        type=Sort.RESPONSE.value,
        channel='some_other_channel',
        parameters=[label_pb2.Label.Parameter(name='param1', value=label_pb2.Label.Parameter.Value(boolean=True))],
        correlation_id=1001,
        physical_label='{a:b}'.encode('UTF-8'),
        timestamp=int(ts.timestamp() * 1e6))

    print()

    assert Label.decode(pb_label) == Label(Sort.RESPONSE,
                                           'some_other_label',
                                           'some_other_channel',
                                           [Parameter('param1', Type.BOOLEAN, True)],
                                           correlation_id=1001,
                                           physical_label='{a:b}',
                                           timestamp=ts)
