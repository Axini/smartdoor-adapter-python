## Description
This project defines a *Python* implementation of a plugin adapter for Axini's standalone SmartDoor application (SUT). 
It connects the Axini Modeling Platform (AMP) to the standalone SmartDoor SUT.

See https://github/axini and the plugin-adapter-protocol repository for some general information on Axini's plugin adapter protocol. Axini's training on "plugin adapters" provides additional and more detailed information.

The software is distributed under the MIT license, see LICENSE.

## Running the adapter
### Prerequisites
This example adapter is depended on Python (>= 3.10) and uses `pip` for its dependency management. The steps below presume that the `python` and `pip` commands are resolvable in your shell.

### Setting it up
- Clone this repository.
- Open a terminal or command prompt.
- (OPTIONAL) Create a separate virtual environment and activate it `python -m venv <name_of_virtual_env_dir>` and `source <name_of_virtual_env_dir>/bin/activate`
- Perform `pip install -r ./requirements.txt`. This should download all the required dependencies.

### Starting the adapter
- Open a terminal or command prompt.
- Run `python src/adapter/plugin_adapter.py -u <adapter url of AMP> -t <authentication token needed by AMP>`.

### Running the tests
- Open a terminal or command prompt.
- Install the test dependencies `pip install -r tests/requirements.txt`.
- Run the tests `pytest tests/`.

### Generating the documentation
- Open a terminal or command prompt.
- Go to `docs/`.
- Run `make html`.
- Documentation is generated under `docs/_build`.

### Some notes on the implementation
The AMP related code is stored in src/adapter/generic and can be used as-is for **any** Python plugin adapter. All SUT specific code (in this case for the SmartDoor SUT) is stored in src/adapter/smartdoor and should be modified for any new SUT.

#### Threads
The main thread of the adapter ensures that messages from AMP are received and handled. The SmartdoorConnection class (in src/adapter/smartdoor) starts a separate thread which is used for the messages from the SmartDoor SUT over the WebSocket connection between the SUT and the adapter. 

The class QThread (in src/adapter/generic) manages a Queue of items and a Thread. Items can be added to the Queue and the Thread processes items from the queue in a FIFO manner. The Queue can also be emptied. The plugin adapter (class AdapterCore in src/adapter/generic) uses two QThreads for (i) handling messages from AMP and (ii) sending messages to AMP. This ensures that messages from AMP (stimuli) and the SUT (responses) are serviced immediately: any resulting message is added to a queue of pending messages which is processed by either one of the two QThreads.

Using a separate QThread for sending the responses to AMP ensures that only a single WebSocket message can be in transit to AMP. 

The QThread for the messages from AMP (Configuration, Ready, stimuli) is needed for a different reason. The processing of actual ProtoBuf messages from AMP may take some (considerable) time. For instance, after a Configuration message, the SUT has to be started and after a Reset message the SUT has to be reset to its initial state. And even the handling of a stimulus at the SUT may take some time. The WebSocket library is single threaded which means that as long as the BrokerConnection's on_message method is being executed, the websocket library cannot handle any new WebSocket message from AMP, including heartbeat (ping) messages. Therefore, the AdapterCore uses a separate QThread to handle ProtoBuf messages from AMP. When a ProtoBuf message is received from AMP, the on_message method calls the AdapterCore's handle_message method which only adds this message to the queue of pending messages. This ensures that the WebSocket thread is always ready to react on new WebSocket messages from AMP.

The plugin adapter and all its threads are set to run forever. No code is added to gracefully terminate the adapter and its threads. Consequently, when terminating the adapter with Ctrl-C, you will observe several Exceptions on the stderr. This is harmless, though.
