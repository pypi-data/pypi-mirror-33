# coding=utf-8
"""
Handles the creation of logger objects
"""
import logging
import multiprocessing
import sys
import threading
import typing
from pathlib import Path

from elib_logging import configure, exc, settings
from elib_logging.handlers import get_console_handler, get_file_handler
from elib_logging.queued_logging_handler import QueuedLoggingHandler
from elib_logging.remove_old_logs import remove_old_log_files
from elib_logging.rotate_logs import rotate_logs


def get_log_file_path(logger_name: str, log_folder_path_as_str: typing.Optional[str] = None) -> str:
    """Returns the path to a log file"""
    log_folder = Path(log_folder_path_as_str or settings.log_dir()).absolute()
    log_folder.mkdir(exist_ok=True)
    log_folder_path = Path(log_folder.joinpath(f'{logger_name}.log')).absolute()
    return str(log_folder_path)


def get_main_logger():
    """Returns the main application logger"""
    logger = logging.getLogger(settings.logger_name())
    if logger.handlers:
        return logger
    log_file_path = get_log_file_path(
        settings.logger_name(),
        settings.log_dir(),
    )
    rotate_logs(log_file_path)
    remove_old_log_files(log_file_path)
    file_handler = get_file_handler(log_file_path)
    console_handler = get_console_handler()
    if hasattr(sys, 'frozen'):
        console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def get_thread_logger(thread_name: str):
    """Returns a logger suited for a thread"""
    logger_name = f'{settings.logger_name()}.thread.{thread_name}'
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
    log_file_path = get_log_file_path(logger.name, settings.log_dir())
    rotate_logs(log_file_path)
    remove_old_log_files(log_file_path)
    file_handler = get_file_handler(log_file_path)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def get_subprocess_logger(logging_queue: multiprocessing.JoinableQueue, subprocess_name: str):
    """Returns a logger suited for a subprocess"""
    logger_name = f'{settings.logger_name()}.subprocess.{subprocess_name}'
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
    log_file_path = get_log_file_path(logger_name, settings.log_dir())
    rotate_logs(log_file_path)
    remove_old_log_files(log_file_path)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(log_file_path))
    logger.addHandler(QueuedLoggingHandler(logging_queue))
    return logger


def get_logger(logging_queue: multiprocessing.JoinableQueue = None):
    """Returns a logger depending on the current environment"""
    configure.check_settings()
    process_name = multiprocessing.current_process().name  # pylint: disable=not-callable
    if process_name == 'MainProcess':
        if threading.current_thread().name == 'MainThread':
            return get_main_logger()

        return get_thread_logger(threading.current_thread().name)

    if logging_queue is None:
        raise exc.MissingQueueError()
    return get_subprocess_logger(logging_queue, process_name)
