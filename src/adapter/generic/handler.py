from abc import ABC, abstractmethod
from typing import List

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

    @abstractmethod
    def start(self, configuration: Configuration):
        """
        Start a new test case

        Args:
            configuration (Configuration): The configuration needed to start testing
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
    def stimulate(self, label: Label) -> str:
        """
        Processes a stimulus of a given label.

        Args:
            label (Label): Label that the Axini Modeling Platform sent

        Returns:
             str: The physical label.
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
    def configuration(self) -> Configuration:
        """
        The configuration needed by the adapter

        Returns:
            Configuration: The configuration required by this adapter.
        """
        pass
