import logging

import websocket


class BrokerConnection:
    """
    This class holds the connection with the Axini Modeling Platform. It is responsible
    for handling the websocket connection.

    The `BrokerConnection` forwards incoming message to the `AdapterCore`.

    Attributes:
        url (str): The websocket URL of the AMP instance that should be connected to.
        token (str): Token to authorize with.
    """

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.adapter_core = None  # callback to adapter; register separately
        self.websocket = None  # reference to websocket; initialized on #connect

    def register_adapter_core(self, adapter_core):
        """
        Set the adapter core object reference. Must be injected after creation because of possible circular dependencies

        Args:
            adapter_core (AdapterCore)
        """
        self.adapter_core = adapter_core

    def connect(self):
        """
        Connect to the Axini Modeling Platform
        """
        logging.info('Connecting to AMP')

        self.websocket = websocket.WebSocketApp(
            self.url,
            on_open=lambda _: self.on_open(),
            on_close=lambda _, close_status_code, close_msg: self.on_close(close_status_code, close_msg),
            on_message=lambda _, msg: self.on_message(msg),
            on_error=lambda _, msg: self.on_error(msg),
            header={'Authorization': 'Bearer {token}'.format(token=self.token)},
        )

        self.websocket.run_forever()

    def on_open(self):
        """
        Callback handler for when the connection with the Axini Modeling Platform is opened.
        """
        logging.info('Successfully opened a connection')
        self.adapter_core.on_open()


    def on_close(self, close_status_code, close_msg):
        """
        Callback handler for when the connection with the Axini Modeling Platform is closed.

        Args:
            close_status_code (int): The status code returned by closing the connection
            close_msg (str): The reason for the connection termination.
        """
        logging.info('WebSocket connection has been closed with code: {code}, with reason: {reason}'
                     .format(code=close_status_code, reason=close_msg))
        self.adapter_core.on_close()


    def on_message(self, message):
        """
        Callback handler for when a message is received from the Axini Modeling Platform.

        Args:
            message (str): The message that was sent by the Axini Modeling Platform.
        """
        logging.debug('Received a message: {msg}'.format(msg=message))
        self.adapter_core.handle_message(message)


    def on_error(self, err):
        """
        Callback handler for when an error occurs with the connection to the Axini Modeling Platform

        Args:
            err (str): Error message
        """
        logging.error('Got a connection error: {error}'.format(error=err))
        self.adapter_core.send_error(err)

        logging.debug('Closing the connection...')
        self.websocket.close()


    def close(self, reason='', code=-1):
        """
        Close the websocket with the given response close code and close reason.

        Args:
            reason (str): The reason for closing the connection (default '')
            code (int): The status code (default -1)
        """
        if self.websocket:
            logging.info('Closing the connection due to: {reason}'.format(reason=reason))
            logging.info('With error code: {code}'.format(code=code))
            self.websocket.close()
        else:
            logging.warning('No websocket initialized to close')


    def send(self, raw_message):
        """
        Sends the given message` to the Axini Modeling Platform

        Args:
            raw_message (str): The message to send to the Axini Modeling Platform
        """
        if not self.websocket:
            logging.warning('No connection to websocket (yet). Is the adapter connected to AMP?')
        else:
            try:
                logging.debug('Sending out message: {msg}'.format(msg=raw_message))
                self.websocket.send(raw_message, websocket.ABNF.OPCODE_BINARY)
                logging.debug('Success send')
            except Exception as e:
                logging.error('Failed sending message, exception: {ex}'.format(ex=e))
