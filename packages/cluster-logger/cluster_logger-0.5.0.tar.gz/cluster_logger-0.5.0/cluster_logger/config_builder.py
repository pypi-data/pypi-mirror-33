# -*- coding: utf-8 -*-
"""Config builder definition. This will build the application properties that are attached to log messages."""

import json
import os
from typing import Dict, List


class FileAccessWrapper:
    """File access object to be injected."""

    def __init__(self, file_name):
        """Set filename.

        Args:
            fileName (str): filename of file to read
        """
        self.file_name = file_name

    def open(self):
        """Open the file."""
        return open(self.file_name, 'r', encoding="UTF-8")


class ConfigBuilder:
    """Builds the properties config that will be attached to log messages.

    Class constant ENV_KEYS are the default properties that will be added to log messages.
    """

    ENV_KEYS = ['HOST',
                'APP_VERSION',
                'LOGGER_VERBOSE',
                'MARATHON_APP_ID',
                'MARATHON_APP_DOCKER_IMAGE']

    ULM_FLUENT_ENV_KEYS = ['ULM_FLUENTD_LABEL_ENVS',
                           'ULM_FLUENTD_HOST',
                           'ULM_FLUENTD_PORT',
                           'ULM_FLUENTD_TAG',
                           'ULM_FLUENTD_BUFFER',
                           'ULM_FLUENTD_TIMEOUT',
                           'ULM_FLUENTD_CLIENT',
                           'ULM_FLUENTD_ENABLE_TIMEMS_FIELD',
                           'ULM_FLUENTD_TIMEMS_FIELD']

    def __init__(self, props={}, env_keys=[], file_access=None):
        """Application properties initialization.

        Args:
            props (dict(str,str)): Application Specific properties.
            env_keys (list(str)): List of Environment keys.
            file_access (FileAccess): File access instance.
        """
        self.props = props
        self.env_keys = list(set().union(ConfigBuilder.ENV_KEYS, env_keys)) if env_keys else ConfigBuilder.ENV_KEYS
        self.file_access = file_access
        self.ulm_env = {}

        self.config = self.build()

    def read_file(self) -> Dict[str, str]:
        """Read application specified JSON file for config.

        Returns:
            dict(str,str): config dict for storing app properties.
        Raises:
            OSError: for file not found.
            ValueError: for file that is not JSON.
            JSONDecodeError: Raised by json lib.

        """
        with self.file_access.open() as f:
            return json.load(f)

    def read_env(self) -> Dict[str, str]:
        """Read environment variables from list of supplied keys.

        Returns:
            dict(str, str): config dict for storing app properties.

        *For keys that do not appear in the environment, None will be returned

        """
        return {key.lower(): os.environ.get(key) for key in self.env_keys}

    @staticmethod
    def read_ulm_env():
        """Read ULM environment and store it for Fluentd setup."""
        return {key: os.environ.get(key) for key in ConfigBuilder.ULM_FLUENT_ENV_KEYS}

    def build(self) -> Dict[str, str]:
        """Build a config dictionary for logging.

        Returns:
            config: dict(str,str)
        Raises:
            see read_file(path)
        Notes:
            Props overwrites environment.
            Props overwrites JSON file.
            Environment overwrites JSON file.
            Props -> Env -> file

        """
        config = {}
        if self.file_access:
            config = self.read_file()
        config = dict(config, **self.read_env())
        if isinstance(self.props, dict):
            config = dict(config, **self.props)

        return config
