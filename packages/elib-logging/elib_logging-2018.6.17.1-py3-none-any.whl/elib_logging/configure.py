# coding=utf-8
"""
Handles library configuration
"""
import os
import sys
import typing

from elib_logging import exc, settings


def setup_logging(logger_name: str,
                  log_file_name: typing.Optional[str] = None,
                  log_dir: typing.Optional[str] = None,
                  log_format_console: typing.Optional[str] = None,
                  log_format_file: typing.Optional[str] = None,
                  backup_count: typing.Optional[int] = None,):
    """Configures elib_logging based on the current executable name"""
    values = [
        (f'{sys.executable}ELIB_LOGGING_LOGGER_NAME', logger_name),
        (f'{sys.executable}ELIB_LOGGING_LOG_FILE_NAME', log_file_name or logger_name),
        (f'{sys.executable}ELIB_LOGGING_LOG_DIR', log_dir or settings.DEFAULT_LOG_DIR),
        (f'{sys.executable}ELIB_LOGGING_LOG_FORMAT_CONSOLE', log_format_console or settings.DEFAULT_LOG_FORMAT_CONSOLE),
        (f'{sys.executable}ELIB_LOGGING_LOG_FORMAT_FILE', log_format_file or settings.DEFAULT_LOG_FORMAT_FILE),
        (f'{sys.executable}ELIB_LOGGING_BACKUP_COUNT', backup_count or settings.DEFAULT_LOG_FILE_BACKUP_COUNT),
    ]
    for val_name, val_value in values:
        os.environ[val_name] = str(val_value)


def check_settings():
    """Raises LoggerNotSetupError if there are missing config values"""
    values = [
        f'{sys.executable}ELIB_LOGGING_LOGGER_NAME',
        f'{sys.executable}ELIB_LOGGING_LOG_FILE_NAME',
        f'{sys.executable}ELIB_LOGGING_LOG_DIR',
        f'{sys.executable}ELIB_LOGGING_LOG_FORMAT_CONSOLE',
        f'{sys.executable}ELIB_LOGGING_LOG_FORMAT_FILE',
        f'{sys.executable}ELIB_LOGGING_BACKUP_COUNT',
    ]
    for val in values:
        if os.getenv(val) is None:
            raise exc.LoggerNotSetupError(f'missing value: {val}')
