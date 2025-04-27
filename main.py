#!/usr/bin/env python3
from src.cli import parse_args
from src.core.processor import LogProcessor
from src.reports.handlers import HandlersReport


def main() -> None:
    args = parse_args()
    processor = LogProcessor(args.log_files)
    
    if args.report == "handlers":
        report = HandlersReport()
        report.generate(processor.process_files())
    else:
        raise ValueError(f"Неизвестный тип отчета: {args.report}")


if __name__ == "__main__":
    main()
