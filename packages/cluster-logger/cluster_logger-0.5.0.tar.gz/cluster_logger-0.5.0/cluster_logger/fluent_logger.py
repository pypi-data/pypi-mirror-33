# -*- coding: utf-8 -*-
"""Fluent implementation of cluster logger."""

from fluent import sender
from typing import Dict


class FluentLogger:
    """Fluent logger definition."""

    def __init__(self, logger: sender, application: str, props: Dict[str, str]):
        """Set logger, application label and application properties.

        Args:
            logger (fluent.sender): Fluent logger object.
            application (str): Name of application sending the log message.
            props (Dict(str, str)): Properties to append to log message.
        """
        self.logger = logger
        self.application = application
        self.props = props

    def log(self, message: str) -> None:
        """Log message through fluent."""
        msg = self.props
        msg['message'] = message
        if not self.logger.emit(self.application, msg):
            print(self.logger.last_error)
            self.logger.clear_last_error()
