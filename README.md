
## Description
This project defines a *Python* implementation of a plugin adapter for Axini's standalone SmartDoor application (SUT). 
It connects the Axini Modeling Platform (AMP) to the standalone SmartDoor SUT.

The software is distributed under the MIT license, see LICENSE

## Running the adapter
### Prerequisites
This example adapter is depended on Python (>= 3.10) and uses `pip` for its dependency management. T
he below steps presume that the `python` and `pip` commands are resolvable in your shell.

### Setting it up
- Clone this repository
- Open a terminal or command prompt
- (OPTIONAL) Create a separate virtual environment `python -m venv <name_of_virtual_env_dir>`
- Perform `pip install -r ./requirements.txt`. This should download all the required dependencies

### Starting the adapter
- Open a terminal or command prompt
- Run `python src/adapter/plugin_adapter.py -u <adapter url of AMP> -t <authentication token needed by AMP>`

### Running the tests
- Open a terminal or command prompt
- Install the test dependencies `pip install -r tests/requirements.txt`
- Run the tests `pytest tests/`

### Generating the documentation
- Open a terminal or command prompt
- Go to `docs/`
- Run `make html`
- Documentation is generated under `docs/_build`