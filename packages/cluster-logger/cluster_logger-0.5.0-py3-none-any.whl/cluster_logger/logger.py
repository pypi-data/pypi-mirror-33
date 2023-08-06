# -*- coding: utf-8 -*-
"""Logger that will handle calling logging through different interfaces.

i.e fluentd, HTTP, or whatever comes later.
"""

import logging
from fluent import asynchandler, handler
from .config_builder import ConfigBuilder, FileAccessWrapper


class WrappedLogger:
    """Wrapper for logger that will append values to log messages."""

    logger = None

    def __init__(self, **kwargs):
        """Set values to be appended to log messages."""
        self.logger = kwargs.pop('logger', self.logger)

        if not self.logger or not hasattr(self.logger, 'log'):
            raise TypeError(
                'Subclasses must specify a logger, not {}'
                .format(type(self.logger))
            )

        self.extras = kwargs

    def log(self, level, message, *args, **kwargs):
        """Convert message to a dict and log."""
        if not isinstance(message, dict):
            message = {'message': message}
        message.update(self.extras)

        return self.logger.log(level, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """Log debug."""
        return self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """Log Info."""
        return self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """Log Warning."""
        return self.log(logging.WARNING, message, *args, **kwargs)

    warn = warning

    def error(self, message, *args, **kwargs):
        """Log Error."""
        return self.log(logging.ERROR, message, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        """Log Exception."""
        return self.log(logging.ERROR, message, *args, exc_info=1, **kwargs)

    def critical(self, message, *args, **kwargs):
        """Log Critical."""
        return self.log(logging.CRITICAL, message, *args, **kwargs)


class ClusterLogger(WrappedLogger):
    """ClusterLogger Class."""

    custom_format = {
        'level': '%(levelname)s',
        'stack_trace': '%(exc_text)s'
    }

    tag = ''
    fluent_host = 'localhost'
    fluent_port = 24224
    fluent_timeout = 3.0
    fluent_async = True
    fluent_verbose = False
    fluent_nanosecond_precision = False
    config = {}

    def __init__(self, name: str, tag='', logger=None,):
        """Init the ClusterLogger. User may pass test logger in."""
        if not logger:
            self.logger = logging.getLogger(name)
            if ClusterLogger.fluent_async:
                self.h = asynchandler.FluentHandler(tag or ClusterLogger.tag,
                                                    ClusterLogger.fluent_host,
                                                    ClusterLogger.fluent_port,
                                                    ClusterLogger.fluent_timeout,
                                                    ClusterLogger.fluent_verbose,
                                                    nanosecond_precision=ClusterLogger.fluent_nanosecond_precision)
            else:
                self.h = handler.FluentHandler(tag or ClusterLogger.tag,
                                               ClusterLogger.fluent_host,
                                               ClusterLogger.fluent_port,
                                               ClusterLogger.fluent_timeout,
                                               ClusterLogger.fluent_verbose,
                                               nanosecond_precision=ClusterLogger.fluent_nanosecond_precision)
            formatter = handler.FluentRecordFormatter(ClusterLogger.custom_format)
            self.h.setFormatter(formatter)
            self.logger.addHandler(self.h)
        else:
            self.logger = logger
        super(ClusterLogger, self).__init__(**ClusterLogger.config)

    @classmethod
    def fromConfig(cls,
                   project: str,
                   application: str,
                   fluent_host='',
                   fluent_port=24224,
                   path='',
                   env_keys=[],
                   properties={},):
        """Init config variables."""
        ulm_env = ConfigBuilder.read_ulm_env()
        file_access = FileAccessWrapper(path) if path else None

        if ulm_env['ULM_FLUENTD_LABEL_ENVS']:
            ulm_env_keys = ulm_env['ULM_FLUENTD_LABEL_ENVS'].replace(' ', '').split(',')
            env_keys = list(set().union(ulm_env_keys, env_keys))

        cls.config = ConfigBuilder(props=properties,
                                   env_keys=env_keys,
                                   file_access=file_access).config

        cls.tag = ulm_env['ULM_FLUENTD_TAG'] or project + '.' + application
        cls.fluent_host = ulm_env['ULM_FLUENTD_HOST'] or fluent_host or cls.config.get('host', 'localhost')
        cls.fluent_host = cls.fluent_host or 'localhost'  # if Host exists on config but is set to None
        cls.fluent_port = int(ulm_env['ULM_FLUENTD_PORT']) if ulm_env['ULM_FLUENTD_PORT'] else fluent_port
        cls.fluent_timeout = float(ulm_env['ULM_FLUENTD_TIMEOUT']) if ulm_env['ULM_FLUENTD_TIMEOUT'] else \
            cls.fluent_timeout
        cls.fluent_async = 'async' in ulm_env['ULM_FLUENTD_CLIENT'].lower() if ulm_env['ULM_FLUENTD_CLIENT'] else \
            cls.fluent_async
        cls.fluent_verbose = cls.config.get('logger_verbose', cls.fluent_verbose) in ['True', 'true', '1']
        del cls.config['logger_verbose']

    def log(self, level, message, *args, **kwargs):
        """Call Base class log method."""
        super(ClusterLogger, self).log(level, message, *args, **kwargs)
