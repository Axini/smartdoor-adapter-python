from adapter.generic.api import configuration_pb2
from adapter.generic.api.configuration import ConfigurationItem
from adapter.generic.api.type import Type


def test_configuration_item_creation():
    assert ConfigurationItem('test', Type.STRING, 'test config item', 'some value')


def test_configuration_item_encoding():
    item = ConfigurationItem('t', Type.STRING, 't', 't')

    assert item.encode() == configuration_pb2.Configuration.Item(
        key='t',
        description='t',
        string='t')


def test_pb_configuration_iteam_can_be_decoded():
    pb_item = configuration_pb2.Configuration.Item(key='config_item', description='some desc', string='some val')

    assert ConfigurationItem.decode(pb_item) == ConfigurationItem('config_item', Type.STRING, 'some desc', 'some val')
