import logging
from datetime import datetime

from generic.api.configuration import ConfigurationItem, Configuration
from generic.api.label import Label, Sort
from generic.api.parameter import Type, Parameter
from generic.handler import Handler as AbstractHandler
from smartdoor.smartdoor_connection import SmartDoorConnection


def _response(name, channel='door', parameters=None):
    return Label(Sort.RESPONSE, name, channel, parameters=parameters)


def _stimulus(name, channel='door', parameters=None):
    return Label(Sort.STIMULUS, name, channel, parameters=parameters)


class Handler(AbstractHandler):
    """
    This class handles the interaction between AMP and the SmartDoor SUT.
    """

    def __init__(self):
        super().__init__()
        self.sut = None

    def send_message_to_amp(self, raw_message: str):
        """
        Send a message back to AMP. The message from the SUT needs to be converted to a Label.

        Args:
            raw_message (str): The message to send to AMP.
        """
        logging.debug('response received: {label}'.format(label=raw_message))

        if raw_message == 'RESET_PERFORMED':
            self.adapter_core.send_ready()
        else:
            message = Label(
                sort=Sort.RESPONSE,
                name=raw_message.lower(),
                channel='door',
                physical_label=bytes(raw_message, 'UTF-8'),
                timestamp=datetime.now())

            self.adapter_core.send_response(message)

    def start(self, configuration: Configuration):
        """
        Start a test.

        Args:
            configuration (Configuration): The configuration to be used for this test run. First item contains the
                url of the SmartDoor SUT.
        """
        self.sut = SmartDoorConnection(self, configuration.items[0].value)
        self.sut.connect()

    def reset(self):
        """
        Prepare the SUT for the next test case.
        """
        logging.info('Resetting the sut for new test cases')
        self.sut.send('RESET')

    def stop(self):
        """
        Stop the SUT from testing.
        """
        logging.info('Stopping the plugin adapter from plugin handler')

        self.sut.stop()
        self.sut = None

        logging.debug('Finished stopping the plugin adapter from plugin handler')

    def stimulate(self, label: Label):
        """
        Processes a stimulus of a given Label message.

        Args:
            label (Label)

        Returns:
            str: The raw message send to the SUT (in a format that is understood by the SUT).
        """
        logging.debug('Stimulate is called, passing the message to the SUT')

        # Convert the message to a message known to the sut
        if label.name in ['lock', 'unlock']:
            sd_msg = '{msg}:{passcode}'.format(msg=label.name.upper(), passcode=label.parameters[0].value)
        else:
            sd_msg = '{msg}'.format(msg=label.name.upper())

        self.sut.send(sd_msg)

        return bytes(sd_msg, 'UTF-8')

    def supported_labels(self):
        """
        The labels supported by the adapter.

        Returns:
             [Label]: List of all supported labels of this adapter
        """
        return [
            _stimulus('open'),
            _response('opened'),
            _stimulus('close'),
            _response('closed'),
            _stimulus('lock', parameters=[Parameter('passcode', Type.INTEGER)]),
            _response('locked'),
            _stimulus('unlock', parameters=[Parameter('passcode', Type.INTEGER)]),
            _response('unlocked'),
            _stimulus('reset'),
            _response('invalid_command'),
            _response('invalid_passcode'),
            _response('incorrect_passcode'),
            _response('shut_off'),
        ]

    def configuration(self):
        """
        The configuration items exposed and needed by this adapter.

        Returns:
            Configuration
        """
        return Configuration([ConfigurationItem(name='endpoint',
                                                tipe=Type.STRING,
                                                description='Base websocket URL of the SmartDoor API',
                                                value='ws://localhost:3001'),
                              ])
