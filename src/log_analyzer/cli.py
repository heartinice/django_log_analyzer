import argparse
import os
from typing import List, NamedTuple


class CliArgs(NamedTuple):
    log_files: List[str]
    report: str


def parse_args() -> CliArgs:
    parser = argparse.ArgumentParser(
        description="Анализатор логов Django-приложения"
    )
    
    parser.add_argument(
        "log_files",
        nargs="+",
        help="Пути к файлам логов для анализа"
    )
    
    parser.add_argument(
        "--report",
        required=True,
        choices=["handlers"],
        help="Тип отчета для генерации"
    )
    
    args = parser.parse_args()
    
    # Проверяем существование файлов
    for log_file in args.log_files:
        if not os.path.exists(log_file):
            raise ValueError(f"Файл лога не существует: {log_file}")
    
    return CliArgs(
        log_files=args.log_files,
        report=args.report
    )