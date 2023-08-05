# coding=utf-8
"""
Cleans up old log files
"""
import typing
from pathlib import Path

from elib_logging import settings


def remove_old_log_files(log_file_path: str, max_count: typing.Optional[int] = None) -> None:
    """
    Removes log files if there are more than a given count

    :param log_file_path: path to the main log file
    """
    log_file = Path(log_file_path).absolute()
    folder = log_file.parent
    if max_count is None:
        max_count = int(settings.backup_count())

    old_logs = sorted(
        [
            x for x in folder.iterdir()
            if x.name.startswith(f'{log_file.stem}.log-')
        ]
    )[:-(max_count - 1)]

    for path in old_logs:
        path.unlink()
