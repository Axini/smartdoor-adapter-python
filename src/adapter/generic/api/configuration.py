from enum import Enum
from typing import List

import generic.api.configuration_pb2 as configuration_pb2
from generic.api.type import Type


class ConfigurationItem:
    """
        This class represents a Configuration Item DTO and has convenient methods to en- and decode to
        Google Protobuf format.

        Attributes:
            name (str): Name of the item
            tipe (Type): Expected type of the item
            description (str): A humanreadable description of the item
            value (int | float | str | bool): Value of the item. Can be of different types.
    """

    def __init__(self, name: str, tipe: Type, description: str, value: int | float | str | bool):
        if not isinstance(tipe, Type):
            raise ValueError('Given tipe should be of the type Type enum')

        if tipe not in [Type.STRING, Type.INTEGER, Type.DECIMAL, Type.BOOLEAN]:
            raise ValueError('Type should either be STRING, INTEGER, DECIMAL or BOOLEAN')

        self.name = name
        self.tipe = tipe
        self.description = description
        self.value = value

    def encode(self):
        """
        Encode the values to a Google Protobuf format
        Returns:
            The DTO encoded in Google Protobuf
        """
        pb_item = None

        if self.tipe == Type.STRING:
            pb_item = configuration_pb2.Configuration.Item(key=self.name,
                                                           description=self.description,
                                                           string=self.value)
        elif self.tipe == Type.INTEGER:
            pb_item = configuration_pb2.Configuration.Item(key=self.name,
                                                           description=self.description,
                                                           integer=self.value)
        elif self.tipe == Type.DECIMAL:
            pb_item = configuration_pb2.Configuration.Item(key=self.name,
                                                           description=self.description,
                                                           float=self.value)
        elif self.tipe == Type.BOOLEAN:
            pb_item = configuration_pb2.Configuration.Item(key=self.name,
                                                           description=self.description,
                                                           boolean=self.value)

        return pb_item

    def __eq__(self, other):
        if isinstance(other, ConfigurationItem):
            return self.__dict__ == other.__dict__

    @classmethod
    def decode(cls, pb_config_item: configuration_pb2.Configuration.Item):
        """
        Factory method that decodes from Google Protobuf format to this DTO

        Args:
            pb_config_item (configuration_pb2.Configuration.Item)

        Returns:
            ConfigurationItem
        """

        tipe = None
        val = None

        if pb_config_item.HasField('string'):
            tipe = Type.STRING
            val = pb_config_item.string
        elif pb_config_item.HasField('integer'):
            tipe = Type.INTEGER
            val = pb_config_item.integer
        elif pb_config_item.HasField('float'):
            tipe = Type.DECIMAL
            val = pb_config_item.float
        elif pb_config_item.HasField('boolean'):
            tipe = Type.BOOLEAN
            val = pb_config_item.boolean
        else:
            raise ValueError('Unsupported configuration item type')

        return ConfigurationItem(pb_config_item.key, tipe, pb_config_item.description, val)


class Configuration:
    """
    Data Transfer Object representing the Configuration object.
    This class allows for the en- and decoding to their Google Protobuf format

    Attributes:
        items ([ConfigurationItem])
    """

    def __init__(self, items: List[ConfigurationItem]):
        self.items = items

    def encode(self):
        """
        Encode to Google Protobuf format

        Returns:
            configuration_pb2.Configuration: Object encoded in Google Protobuf format

        """
        return configuration_pb2.Configuration(items=[item.encode() for item in self.items])

    @classmethod
    def decode(cls, pb_config: configuration_pb2.Configuration):
        """
        Factory method that decodes from Google Protobuf format to this DTO

        Args:
            pb_config (configuration_pb2.Configuration): The configuration in Google Protobuf format

        Returns:
            Configuration: The configuration as a DTO
        """
        return Configuration([ConfigurationItem.decode(pb_item) for pb_item in pb_config.items])
