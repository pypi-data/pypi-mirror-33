# -*- coding: utf-8 -*-
"""Get a Cluster Logger object."""

from .logger import ClusterLogger


__version__ = '0.5.0'


def initLogger(project: str,
               application: str,
               fluent_host='',
               fluent_port=24224,
               path='',
               env_keys=[],
               properties={},):
    """Create the config for log messages."""
    ClusterLogger.fromConfig(project,
                             application,
                             fluent_host,
                             fluent_port,
                             path,
                             env_keys,
                             properties,)


def getLogger(name: str, is_metric=False) -> ClusterLogger:
    """Get a logger."""
    tag = ''
    if is_metric:
        tag = ClusterLogger.tag + '.metrics'
    return ClusterLogger(name, tag=tag)
