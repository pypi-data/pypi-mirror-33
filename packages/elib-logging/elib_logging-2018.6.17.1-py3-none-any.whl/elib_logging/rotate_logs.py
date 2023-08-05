# coding=utf-8
"""
Handles log files rotation
"""
import datetime
from pathlib import Path


def rotate_logs(log_file_path: str) -> None:
    """
    Archive previous log file if it exists

    :param log_file_path: path to the log file to archive
    """
    log_file = Path(log_file_path).absolute()
    if log_file.exists():
        now = datetime.datetime.now().isoformat().replace(':', '').split('.')[0]
        new_name = f'{log_file.stem}.log-{now}'
        folder = log_file.parent
        new_path = Path(folder, new_name).absolute()
        log_file.rename(new_path)
