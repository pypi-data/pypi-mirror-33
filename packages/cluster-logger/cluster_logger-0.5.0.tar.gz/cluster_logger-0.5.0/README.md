# Cluster Logging library for python 3.6

This is a library for python 3.6 that will help fulfil a
requirement for cluster services and logging to elastic search.

## Requirements

-   Python 3.6+
-   pipenv
-   Elasticsearch
-   Fluentd
-   Kibana

## Pipenv & Pipfile

Pipenv combines package management and virtualenv into one tool.  
pipenv: https://docs.pipenv.org/basics

To install:

```bash
$ pip install pipenv
```

Pipfile replaces requirements.txt and it will specify both dependencies and dev dependencies in one file.

## Development Installation

```bash
# install dependencies
pipenv install --dev

# activate virtual environment
pipenv shell

# alternativly you can start your script in a virtual environment context
pipenv run python main.py message that you want to send
```

## ULM Configuration

The default configuration uses Environment variables to configure the logger.  
These values were grabbed from version 2.0 of ULM-logging-common Java implementation. Not every value is implemented yet and changes are upto date in table.  
[Repo](https://bitbucket.di2e.net/projects/PIR/repos/logging-common/browse)

| Variable | Default Value | Description | Implemented |
| -------- | ------------- | ----------- | ----------: |
| ULM_FLUENTD_HOST | localhost | host of the FluentD service | ✔️
| ULM_FLUENTD_PORT | 24224 | port of FluentD tcp "in_forward" | ✔️
| ULM_FLUENTD_LABEL_ENVS |  | comma separated list(with or without space) of other ENV vars to add as fields to FluentD logs | ✔️
| ULM_FLUENTD_TAG | (project).(app) | tag to use when sending logs to fluentd, e.g. the MLA_IDENT string such as "Myapp.logs" | ✔️
| ULM_FLUENTD_BUFFER | 1048576 | an integer of the number of bytes to allow in the buffer.  Excess will be dropped (default is 1MiB) | ❌
| ULM_FLUENTD_TIMEOUT | 3.0 | an float of the number of ms to allow for communication with FluentD. | ✔️
| ULM_FLUENTD_CLIENT | async |  Whether to send async messages or not. This will send async as long as the value has async somewhere in the string. | ✔️
| ULM_FLUENTD_ENABLE_TIMEMS_FIELD | False | Enables an additional field to contain the millisecond timestamp | ❌
| ULM_FLUENTD_TIMEMS_FIELD |  timems  | the name of the field to contain the millisecond timestamp | ❌

## Standalone Usage (Development)

It may be required to run the following command to get elastic search to run.

```bash
sudo sysctl -w vm.max_map_count=262144
```

### Local

```bash
$ pipenv run python main.py -h
usage: main.py [-h] [-n HOST] [-p PORT] [-e [ENV [ENV ...]]] [-o PROJECT]
               [-a APP] [-c COUNT]

Console Application to test Cluster Logging using fluentd.

positional arguments:
  message               Message to be logged.

optional arguments:
  -h, --help            show this help message and exit
  -n HOST, --host HOST  Hostname to listen on. (default=localhost)
  -p PORT, --port PORT  Port number to bind to. (default=24224)
  -e [ENV [ENV ...]], --env [ENV [ENV ...]]
                        Environment Keys to add to message.
  -o PROJECT, --project PROJECT
                        Tag for the project
  -a APP, --app APP     Tag for the application
  -c COUNT, --count COUNT
                        The number of times to send message.
```

### Docker

```bash
$ docker build -t TAG_FOR_THE_BUILD:VERSION .

# all env values can be set with -e

$ docker run -e host=fluentd \
  -e port=24224 -e msg="message you want to send" TAG_FOR_THE_BUILD:VERSION

# If you want to run the whole environment you can use docker-compose up

$ docker-compose up
```

### Api

Follows the python logger implementation with logging levels. [python.org](https://docs.python.org/3/library/logging.html)

| Level    | Numeric value |
| -------- | ------------: |
| CRITICAL |            50 |
| ERROR    |            40 |
| WARNING  |            30 |
| INFO     |            20 |
| DEBUG    |            10 |
| NOTSET   |             0 |

Logging level can be set for logging using:

```python
import logging
logging.basicConfig(level=logging.WARNING)
```

Setting the logging level will filter levels below the set logging level. For logging levels error and above the stack trace will be added to the log message.

### Standard Configuration

These environment variables can be set either system-wide or added to the `.env` file:

There are 3 Environment variables that will be extracted by default:

-   `HOST` - host that the container is running on.
-   `APP_VERSION` - Version of the app.
-   `LOGGER_VERBOSE` - Whether the fluent logger library is verbose or not.
-   `MARATHON_APP_ID` - The ID that is assigned by DCOS.
-   `MARATHON_APP_DOCKER_IMAGE` - The image that the container was built from.

There are three ways to get application properties into log messages.

-   pass a dictionary of key value pairs
-   pass a list of keys that are on the container environment
-   or pass a JSON file with key value pairs.

NOTE:

-   The dictionary will overwrite values in environment and JSON file.
-   The Environment will overwrite values in the JSON file.

### Usage

Activate your venv

```bash
# Linux / MacOS
source {NAME_OF_VENV}/bin/activate
```

```bat
REM Windows
{NAME_OF_VENV}\Scripts\activate
```

Install cluster logger into your venv. Cluster Logger has been installed into pypi.

```bash
$ pip install cluster_logger
```

To Use

```python
import cluster_logger
import logging
# Then init the ClusterLogger class

env_keys = ['MARATHON_APP_LABELS', 'MARATHON_APP_RESOURCE_CPUS']
props = {'HOST', '192.168.0.12'}

logging.basicConfig(level=logging.DEBUG)             # set logging level
cluster_logger.initLogger('Rasters',                 # Project name
                          'intent_client',           # Application name
                          'fluentd',                 # Fluentd Host name (optional) will default to fluentd if nothing is passed in and HOST isn't set on the environment
                          24224,                     # Fluentd Port Number(optional)
                          '/path/to/settings.json',  # JSON settings file (optional)
                          env_keys,                  # Environment Keys (optional)
                          props)                     # Specific Properties (optional)

# in Module where you will log
import cluster_logger

# General Logger
logger = cluster_logger.getLogger(__name__)
# Metric Logger
metrics = cluster_logger.getLogger(__name__ + '.metrics', is_metric=True)

logger.exception('Custom Message to send typically an error')
logger.log(logging.INFO, {'Duration', 58})
```

### Contributing

```bash
# bump the version that is stored in setup.py and cluster_logger/__init__.py
# assuming pipenv install --dev was ran first
$ pipenv run bumpversion minor # possible: major / minor / patch
$ git push
```
