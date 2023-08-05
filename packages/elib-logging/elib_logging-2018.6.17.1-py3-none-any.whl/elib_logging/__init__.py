# coding=utf-8
"""
Handles logging for an application or a library
"""

from elib_logging.configure import setup_logging
from elib_logging import exc
from elib_logging.logger import get_logger

__all__ = ['setup_logging', 'get_logger', 'exc']
