# coding=utf-8
"""
Handles settings retrieval from os.environ
"""
import os
import sys

from elib_logging import exc

DEFAULT_LOG_DIR = './logs'
DEFAULT_LOG_FILE_BACKUP_COUNT = 7
DEFAULT_LOG_FORMAT_FILE = '%(relativeCreated)10d ms ' \
                          '%(processName)15s ' \
                          '%(threadName)15s ' \
                          '%(levelname)8s ' \
                          '%(name)s ' \
                          '[%(pathname)s@%(lineno)d %(funcName)s]: ' \
                          '%(message)s'
DEFAULT_LOG_FORMAT_CONSOLE = '%(relativeCreated)10d ms ' \
                             '%(levelname)8s: ' \
                             '%(message)s'


def _get_value(val_name) -> str:
    sys_val_name = f'{sys.executable}{val_name}'
    val_value = os.getenv(sys_val_name)
    if val_value is None:
        raise exc.LoggerNotSetupError(f'missing value: {val_name}')
    return val_value


def logger_name() -> str:
    """Returns the main logger name"""
    return _get_value('ELIB_LOGGING_LOGGER_NAME')


def log_file_name() -> str:
    """Returns the name of the base log file"""
    return _get_value('ELIB_LOGGING_LOG_FILE_NAME')


def log_dir() -> str:
    """Returns the logs folder"""
    return _get_value('ELIB_LOGGING_LOG_DIR')


def log_format_console() -> str:
    """Returns the format strings for console records"""
    return _get_value('ELIB_LOGGING_LOG_FORMAT_CONSOLE')


def log_format_file() -> str:
    """Returns the format string for file records"""
    return _get_value('ELIB_LOGGING_LOG_FORMAT_FILE')


def backup_count() -> str:
    """Returns the amount of log files to keep"""
    return _get_value('ELIB_LOGGING_BACKUP_COUNT')
