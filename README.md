# Robotic Researcher
Hello Quandri Hiring team, welcome to your technical test review. 
Hope you have a good experience reviewing this test (:

This project is a script that retrieves information about a person, or people, from Wikipedia. 
This can be used to gather data for research, education, or any other purpose where such information might be useful.

## How to use
### Requirements
- [python](https://www.python.org/downloads/)

Optional:
- [pyenv](https://github.com/pyenv/pyenv)


### Instaling requirements
To run the script locally you'll need to:
1. create a virtual environment to isolate the project.  
2. install the dependencies.  

```shell
$ python -m virtualenv venv
$ source .venv/bin/activate
$ make dependencies 
```

### Running the script
To get the help on how to properly use the script you can use `--help`
```shell
$ python main.py --help
usage: main.py [-h] [-H] [-S] [-o OUTPUT_PATH] [-f {txt,csv,json}] people

Retrieve information about people from Wikipedia.

positional arguments:
  people                People you want to search for separated by comma ',' i.e. 'Albert Einstin, Isaac Newton, Marie Curie'.

options:
  -h, --help            show this help message and exit
  -H, --headless        Run the browser in headless mode.
  -S, --silent          Run bot in silent mode (no terminal output).
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path for a file to output the results to.
  -f {txt,csv,json}, --format {txt,csv,json}
                        Output format. Can be 'txt','csv' or 'json'. Default is 'csv'.
```


### Testing
To execute tests you'll need to install the `dev-dependencies` then you can use the `make test-coverage` when inside the local virtual environment.
```shell
$ source .venv/bin/activate  # if not in the venv already
$ make dev-dependencies 
$ make test-coverage
```

### Commands
To get a general help on how to execute this you can use `make` in the root folder to get the `--help` information from the Makefile.
```shell
$ make
Help documentation for this project

Usage:
  make [command] 

Commands:
ci-dependencies      Install dependencies using pip
clean                Clean bloat files from project
clean-build          Clean build files
clean-eggs           Remove egg files
dependencies         Install dependencies
dev-dependencies     Install dev and main dependencies
format-code          Format code
help                 Display this help
lint                 Check code lint
outdated             Show outdated packages
set-path             Set Python Path
test                 Run tests
test-coverage        Run tests with coverage output
test-coverage-unit   Run unit tests with coverage output
test-debug           Run tests with active pdb
test-unit            Run unit tests
```
