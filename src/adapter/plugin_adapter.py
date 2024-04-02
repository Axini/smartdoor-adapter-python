import argparse
import logging
import socket

from generic.adapter_core import AdapterCore
from generic.broker_connection import BrokerConnection
from smartdoor.handler import Handler

ADAPTER_NAME = 'Smartdoor'

def start_plugin_adapter(adapter_name: str, url: str, token: str, loglevel: int):
    """
    Start the adapter and connect with AMP.

    Args:
        adapter_name (str): Name of the adapter
        url (str): Url of the Axini Modeling Platform
        token (str): Token needed to authenticate with the Axini Modeling Platform
        loglevel (int): Loglevel constant
    """
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s-[%(levelname)8s] %(name)s::%(module)s|%(lineno)s:: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    broker_connection = BrokerConnection(url, token)
    handler = Handler()

    adapter_core = AdapterCore(adapter_name, broker_connection, handler)

    broker_connection.register_adapter_core(adapter_core)
    handler.register_adapter_core(adapter_core)

    adapter_core.start()

if __name__ == '__main__':
    print("Parsing arguments")
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name',
                        help='Adapter name suffix visible in AMP: "some_suffix" (optional)', required=False)
    parser.add_argument('-u', '--url',
                        help='AMP Adapter URL reference: "wss://..."', required=True)
    parser.add_argument('-t', '--token',
                        help='AMP Adapter Token: "kjhsdkhk..."', required=True)
    parser.add_argument('-ll', '--log_level',
                        help='AMP Adapter logger level: ERROR, WARNING, INFO, DEBUG (default: INFO)',
                        required=False)

    args = parser.parse_args()

    # Create the name as displayed on the adapter page of AMP
    suffix = socket.gethostname()
    if args.name:
        suffix = args.name

    name = ADAPTER_NAME + "@" + suffix

    if not args.log_level:
        log_level = logging.INFO
    else:
        log_level = args.log_level

    start_plugin_adapter(name, args.url, args.token, log_level)
