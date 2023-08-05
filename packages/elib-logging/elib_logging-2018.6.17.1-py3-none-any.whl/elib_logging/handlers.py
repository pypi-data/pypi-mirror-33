# coding=utf-8
"""
Handles the creation of logging handlers
"""
import logging
import sys

from elib_logging.formatter import get_console_formatter, get_file_formatter


def get_file_handler(log_file_path: str, formatter: logging.Formatter = None) -> logging.Handler:
    """
    Returns a handler for logging files

    :param log_file_path: path to the log file
    :param formatter: logging formatter for this handler
    :return: logging handler
    """
    if formatter is None:
        formatter = get_file_formatter()
    handler = logging.FileHandler(filename=log_file_path, mode='w', encoding='utf8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def get_console_handler(formatter: logging.Formatter = None) -> logging.Handler:
    """
    Returns a handler for logging streams

    :param formatter: logging formatter for this handler
    :return: logging handler
    """
    if formatter is None:
        formatter = get_console_formatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler
