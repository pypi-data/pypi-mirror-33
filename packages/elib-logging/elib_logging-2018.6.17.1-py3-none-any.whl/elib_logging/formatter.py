# coding=utf-8
"""
Handles the creation of logging formatters
"""
import logging
import sys

from elib_logging import settings


def get_formatter(log_format: str) -> logging.Formatter:
    """
    Creates a logging formatter

    :param log_format: format string to use
    :return: logging formatter
    """
    return logging.Formatter(log_format)


def get_console_formatter() -> logging.Formatter:
    """
    Returns a logging formatter for a stream handler

    The function uses a different format if the application is frozen

    :return: logging formatter
    """
    if hasattr(sys, 'frozen'):
        return get_formatter(settings.log_format_console())
    return get_file_formatter()


def get_file_formatter() -> logging.Formatter:
    """
    Returns a logging formatter for a file handler

    :return: logging formatter
    """
    return get_formatter(settings.log_format_file())
