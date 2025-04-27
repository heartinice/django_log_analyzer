import os
import pytest
from typing import List, Dict
from src.core.parser import LogParser
from src.core.processor import LogProcessor
from src.reports.handlers import HandlersReport
from src.cli import parse_args


def create_test_log(tmp_path, content: str) -> str:
    log_file = tmp_path / "test.log"
    log_file.write_text(content)
    return str(log_file)


@pytest.fixture
def sample_logs() -> Dict[str, str]:
    return {
        'info': '2025-03-27 12:36:45,000 INFO django.request: GET /api/v1/checkout/ 201 OK [192.168.1.62]',
        'error': '2025-03-27 12:33:05,000 ERROR django.request: Internal Server Error: /api/v1/users/ [192.168.1.39]',
        'warning': '2025-03-27 12:35:19,000 WARNING django.request: GET /api/v1/checkout/ 400 Bad Request [192.168.1.39]',
        'debug': '2025-03-27 12:42:07,000 DEBUG django.request: GET /api/v1/users/ 201 OK [192.168.1.22]',
        'critical': '2025-03-27 12:44:47,000 CRITICAL django.request: GET /api/v1/payments/ 503 Service Unavailable [192.168.1.57]'
    }


class TestLogParser:
    
    def test_parse_info_request(self, sample_logs):
        parser = LogParser()
        result = parser._parse_line(sample_logs['info'])
        
        assert result is not None
        assert result['level'] == 'INFO'
        assert result['logger'] == 'django.request'
        assert result['path'] == '/api/v1/checkout/'

    def test_parse_error_request(self, sample_logs):
        parser = LogParser()
        result = parser._parse_line(sample_logs['error'])
        
        assert result is not None
        assert result['level'] == 'ERROR'
        assert result['logger'] == 'django.request'
        assert result['path'] == '/api/v1/users/'

    def test_parse_all_log_levels(self, sample_logs):
        parser = LogParser()
        for log_line in sample_logs.values():
            result = parser._parse_line(log_line)
            assert result is not None
            assert 'path' in result
            assert result['path'] is not None


class TestLogProcessor:
    
    def test_process_single_file(self, tmp_path, sample_logs):
        # Создаем файл с одной записью каждого уровня
        content = '\n'.join(sample_logs.values())
        log_file = create_test_log(tmp_path, content)
        
        processor = LogProcessor([log_file])
        result = processor.process_files()
        
        assert len(result) == 5 

    def test_process_multiple_files(self, tmp_path, sample_logs):
        content1 = '\n'.join([sample_logs['info'], sample_logs['error']])
        content2 = '\n'.join([sample_logs['debug'], sample_logs['critical']])
        
        file1 = tmp_path / "app1.log"
        file2 = tmp_path / "app2.log"
        file1.write_text(content1)
        file2.write_text(content2)
        
        processor = LogProcessor([str(file1), str(file2)])
        result = processor.process_files()
        
        assert len(result) == 4  # Общее количество записей из обоих файлов


class TestHandlersReport:

    def test_report_format(self, tmp_path, sample_logs):
        content = '\n'.join(sample_logs.values())
        log_file = create_test_log(tmp_path, content)
        
        processor = LogProcessor([log_file])
        report = HandlersReport()
        log_data = processor.process_files()
        stats = report._aggregate_stats(log_data)
        
        assert 'total' in stats
        assert 'stats' in stats
        assert isinstance(stats['stats'], dict)
        
        for handler_stats in stats['stats'].values():
            for level in report.LOG_LEVELS:
                assert level in handler_stats

    def test_handlers_sorting(self, tmp_path, sample_logs):
        content = '\n'.join(sample_logs.values())
        log_file = create_test_log(tmp_path, content)
        
        processor = LogProcessor([log_file])
        report = HandlersReport()
        log_data = processor.process_files()
        stats = report._aggregate_stats(log_data)
        
        handlers = list(stats['stats'].keys())
        sorted_handlers = sorted(handlers)
        assert set(handlers) == set(sorted_handlers)
        
        from io import StringIO
        import sys
        
        stdout = StringIO()
        sys.stdout = stdout
        
        report._print_report(stats)
        
        sys.stdout = sys.__stdout__
        
        output = stdout.getvalue()
        
        output_lines = output.split('\n')
        
        handlers_in_output = [
            line.split('\t')[0].strip() 
            for line in output_lines[3:-2]  # Изменили срез
            if line.strip() and not line.startswith('HANDLER')  # Добавили фильтр
        ]
        
        assert handlers_in_output == sorted(handlers_in_output), \
            f"Handlers are not sorted. Got: {handlers_in_output}"


def test_cli_arguments(tmp_path, sample_logs):
    log_file = create_test_log(tmp_path, sample_logs['info'])
    
    test_args = ['main.py', log_file, '--report', 'handlers']
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('sys.argv', test_args)
        args = parse_args()
        assert args.log_files == [log_file]
        assert args.report == 'handlers'

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('sys.argv', ['main.py', 'non_existent.log', '--report', 'handlers'])
        with pytest.raises(ValueError):
            parse_args()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('sys.argv', ['main.py', log_file, '--report', 'invalid'])
        with pytest.raises(SystemExit):
            parse_args()
