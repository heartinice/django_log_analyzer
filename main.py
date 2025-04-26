#!/usr/bin/env python3
from src.log_analyzer.cli import parse_args
from src.log_analyzer.core.processor import LogProcessor
from src.log_analyzer.reports.handlers import HandlersReport


def main() -> None:
    """
    Основная точка входа в приложение.
    Парсит аргументы командной строки и запускает обработку логов.
    """
    args = parse_args()
    processor = LogProcessor(args.log_files)
    
    if args.report == "handlers":
        report = HandlersReport()
        report.generate(processor.process_files())
    else:
        raise ValueError(f"Неизвестный тип отчета: {args.report}")


if __name__ == "__main__":
    main()
