import logging

from abc import ABC, abstractmethod
from typing import List

from generic.api import label_pb2
from generic.api.configuration import Configuration
from generic.api.label import Label

class Handler(ABC):
    """
    Abstract handler. This class needs to be extended by a SUT specific implementation.
    """

    def __init__(self):
        self.adapter_core = None  # callback to adapter; register separately

    def register_adapter_core(self, adapter_core):
        """
        Set the adapter core object reference.

        Args:
            adapter_core (AdapterCore): Reference to the adapter core
        """
        self.adapter_core = adapter_core
        self.configuration = self.default_configuration()

    def set_configuration(self, configuration: Configuration):
        """ Set the configuration of the adapter. """
        self.configuration = configuration

    def get_configuration(self) -> Configuration:
        """ The current configuration of the adapter. """
        return self.configuration

    @abstractmethod
    def start(self):
        """
        Start a new test case.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Prepare the SUT for the next test case.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop the SUT from testing.
        """
        pass

    @abstractmethod
    def stimulate(self, pb_label: label_pb2.Label):
        """
        Processes a stimulus of a given label at the SUT.

        Args:
            pb_label (label_pb2.Label): stimulus that the Axini Modeling Platform has sent
        """
        pass

    @abstractmethod
    def supported_labels(self) -> List[Label]:
        """
        The labels supported by the adapter.

        Returns:
            [Label]: The supported labels.
        """
        pass

    @abstractmethod
    def default_configuration(self) -> Configuration:
        """
        The default configuration of this adapter.

        Returns:
            Configuration: the default configuration required by this adapter.
        """
        pass
