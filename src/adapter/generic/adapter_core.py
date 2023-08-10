import logging
import time
from enum import Enum
from typing import List

from .api import label_pb2, message_pb2, announcement_pb2, configuration_pb2
from .api.configuration import Configuration
from .api.label import Label
from .broker_connection import BrokerConnection
from .handler import Handler


class State(Enum):
    """
    Enumeration describing the different state the adapter can be in.
    """
    DISCONNECTED = 0
    CONNECTED = 1
    ANNOUNCED = 2
    CONFIGURED = 3
    READY = 4
    ERROR = 9


class AdapterCore:
    """
    This class implements the core of a plugin-adapter. It handles the connection
    to the broker (`BrokerConnection`) and the connection to the sut (via the `Handler`).
    Initially the adapter is in a DISCONNECTED state.

    Attributes:
        name (str): The communicated name of this adapter
        broker_connection (BrokerConnection): The broker connection does the communication to AMP
        handler (adapter.generic.handler.Handler): The handler that handles the communication to the SUT
    """

    def __init__(self, name: str, broker_connection: BrokerConnection, handler: Handler):
        self.name = name
        self.broker_connection = broker_connection
        self.handler = handler
        self.state = State.DISCONNECTED

    def start(self):
        """ Start the adapter core which will open a connection with AMP. """
        if self.state == State.DISCONNECTED:
            logging.info('Connecting to broker')
            self.broker_connection.connect()
        else:
            logging.info('Connection started while already connected')

    def on_open(self):
        """ Broker call back for when the connection is opened with AMP. """
        if self.state == State.DISCONNECTED:
            self.state = State.CONNECTED

            self.send_announcement(self.name, self.handler.supported_labels(), self.handler.configuration())
            self.state = State.ANNOUNCED
        else:
            logging.info('Connection opened while already connected')

    def on_close(self):
        """ Connection with AMP has been closed. Try to reconnect. """
        self.state = State.DISCONNECTED
        self.handler.stop()
        logging.info('Trying to reconnect to AMP.')
        self.start() # reconnect to AMP - keep the adapter alive

    def on_configuration(self, pb_config: configuration_pb2.Configuration):
        """
        Broker call back when a `Configuration` message is received from AMP.

        Args:
            pb_config (configuration_pb2.Configuration)
        """
        if self.state == State.ANNOUNCED:
            logging.info('Configuration received')
            self.state = State.CONFIGURED

            # Start the SUT
            logging.info('Connecting to the SUT')
            try:
                self.handler.start(Configuration.decode(pb_config))
            except Exception as e:
                logging.error('Error connection to the SUT: {}'.format(e))
                self.send_error(str(e))
                return
        elif self.state == State.CONNECTED:
            message = 'Configuration received while not yet announced'
            logging.error(message)
            self.send_error(message)
        else:
            message = 'Configuration received while already configured'
            logging.error(message)
            self.send_error(message)

    def on_label(self, pb_label: label_pb2.Label):
        """
        Broker call back when a Label message is received from AMP.

        Args:
            pb_label (label_pb2.Label)
        """
        if self.state == State.READY:
            physical_label = None

            if pb_label.type != label_pb2.Label.LabelType.STIMULUS:
                message = 'Label is not a stimulus'
                logging.error(message)
                self.send_error(message)

            try:
                # Perform the stimulus action which could trigger a response.
                logging.debug('Stimulating label: {label}'.format(label=pb_label.label))
                physical_label = self.handler.stimulate(Label.decode(pb_label))
            except Exception as e:
                logging.error('Exception: {ex}'.format(ex=e))
                self.send_error('error while stimulating the SUT: {ex}'.format(ex=e))

            # Confirm the label
            logging.debug('Confirming stimulus label: {label}'.format(label=pb_label.label))

            pb_label.physical_label = physical_label
            pb_label.timestamp = time.time_ns()

            self._confirm_stimulus(pb_label)
        else:
            message = 'Label received from AMP while not ready'
            logging.error(message)
            self.send_error(message)

    def on_reset(self):
        """ Broker call back when a Reset message is received. """
        if self.state == State.READY:
            logging.debug('Reset message received')

            try:
                response = self.handler.reset()

                if response:
                    message = 'Resetting the SUT failed due to: {reason}'.format(reason=response)
                    logging.error(message)
                    self.send_error(message)
                    return
            except Exception as e:
                message = 'Error while resetting connection to the SUT: {reason}'.format(reason=str(e))
                logging.error(message)
                self.send_error(message)
                return
        else:
            message = 'Reset received while not ready'
            logging.error(message)
            self.send_error(message)

    def on_error(self, message: str):
        """
        Broker call back when a Error message is received.

        Args:
            message (str): The error message
        """
        self.state = State.ERROR

        logging.error('Error message received: {msg}'.format(msg=message))

        # NOTE: we do not send an error message back.
        self.broker_connection.close(reason=message)

    def send_error(self, message: str):
        """
        Send an error to the broker_connection and close the connection

        Args:
            message (str): Send an error message to AMP
        """
        self._send_message(message_pb2.Message(error=message_pb2.Message.Error(message=message)))
        self.broker_connection.close(reason=message)

    def send_response(self, label: Label):
        """
        Send the response from the SUT back to AMP

        Args:
            label (Label): Label to be sent back to AMP
        """
        pb_label = label.encode()

        if pb_label.type == label_pb2.Label.LabelType.RESPONSE:
            self._send_message(message_pb2.Message(label=pb_label))
        else:
            message = 'Label is not of type Response'
            logging.error(message)
            self.send_error(message)

    def _confirm_stimulus(self, pb_label):
        """
        Confirm a received stimulus by sending it back to AMP.

        Args:
            pb_label (label_pb2.Label)
        """
        logging.debug('Sending stimulus (back) to AMP')
        self._send_message(message_pb2.Message(label=pb_label))

    def send_ready(self):
        """
        Let AMP know the adapter is ready to start testing
        """

        logging.debug('Sending ready')
        self._send_message(message_pb2.Message(ready=message_pb2.Message.Ready()))
        self.state = State.READY

    def send_announcement(self, name: str, supported_labels: List[Label], configuration: Configuration):
        """
        Send an announcement to AMP to let the platform know this adapter is available.

        Args:
            name (str): Name of the adapter
            supported_labels ([Label]): Labels supported by this adapter
            configuration (Configuration): Configuration items needed by this adapter
        """

        logging.info('Announcing')

        pb_configuration = configuration.encode()
        pb_supported_labels = [label.encode() for label in supported_labels]
        pb_announcement = announcement_pb2.Announcement(
            name=name, labels=pb_supported_labels, configuration=pb_configuration
        )

        self._send_message(message_pb2.Message(announcement=pb_announcement))

    def handle_message(self, raw_message:str):
        """
        Handle the message coming in from AMP

        Args:
            raw_message (str): Raw string message from AMP.
        """

        pb_message = message_pb2.Message()

        try:
            pb_message.ParseFromString(raw_message)
        except Exception as e:
            logging.error('Could not decode message due to: {ex}'.format(ex=e))

        if pb_message.HasField('configuration'):
            logging.debug('Received a configuration')
            self.on_configuration(pb_message.configuration)
        elif pb_message.HasField('error'):
            logging.debug('Received an error')
            self.on_error(pb_message.error.message)
        elif pb_message.HasField('label'):
            logging.debug('Received a label')
            self.on_label(pb_message.label)
        elif pb_message.HasField('reset'):
            logging.debug('Received a reset')
            self.on_reset()
        elif pb_message.HasField('ready'):
            logging.debug('Received ready, this should not be send')
        else:
            logging.debug('Unknown message type: {msg}'.format(msg=pb_message))

    def _send_message(self, message: message_pb2.Message):
        """
        Convenient method that calls the broker to send a message to AMP

        Args:
            message (message_pb2.Message)
        """
        self.broker_connection.send(message.SerializeToString())
