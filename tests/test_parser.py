from src.log_analyzer.core.parser import LogParser
import pytest
from datetime import datetime


def test_parse_valid_request_log():
    parser = LogParser()
    log_line = '2025-03-27 12:36:45,000 INFO django.request: GET /api/v1/checkout/ 201 OK [192.168.1.62]'
    
    result = parser._parse_line(log_line)
    
    assert result is not None
    assert result['level'] == 'INFO'
    assert result['logger'] == 'django.request'
    assert result['path'] == '/api/v1/checkout/'
    assert result['method'] == 'GET'
    assert result['status'] == 201


def test_parse_invalid_log():
    parser = LogParser()
    log_line = 'Invalid log line format'
    
    result = parser._parse_line(log_line)
    
    assert result is None


def test_parse_different_http_methods():
    """Тест различных HTTP методов"""
    parser = LogParser()
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    for method in methods:
        log_line = f'2025-03-27 12:36:45,000 INFO django.request: {method} /api/v1/test/ 200 OK [192.168.1.62]'
        result = parser._parse_line(log_line)
        
        assert result is not None
        assert result['method'] == method
        assert result['path'] == '/api/v1/test/'
        assert result['status'] == 200


def test_parse_error_log():
    """Тест парсинга лога с ошибкой"""
    parser = LogParser()
    log_line = '2025-03-27 12:33:05,000 ERROR django.request: Internal Server Error: /api/v1/users/ [192.168.1.39]'
    
    result = parser._parse_line(log_line)
    
    assert result is not None
    assert result['level'] == 'ERROR'
    assert result['logger'] == 'django.request'
    assert result['path'] == '/api/v1/users/'
    assert result['method'] == 'ERROR'


def test_parse_non_request_log():
    """Тест парсинга лога не связанного с запросами"""
    parser = LogParser()
    log_line = '2025-03-27 12:36:45,000 INFO django.db: Database query completed in 0.005s'
    
    result = parser._parse_line(log_line)
    
    assert result is not None
    assert result['level'] == 'INFO'
    assert result['logger'] == 'django.db'
    assert result['message'] == 'Database query completed in 0.005s'
    assert 'path' not in result
    assert 'method' not in result


def test_parse_timestamp():
    """Тест парсинга временной метки"""
    parser = LogParser()
    log_line = '2025-03-27 12:36:45,000 INFO django.request: GET /api/v1/test/ 200 OK'
    
    result = parser._parse_line(log_line)
    
    assert result is not None
    assert isinstance(result['timestamp'], datetime)
    assert result['timestamp'].year == 2025
    assert result['timestamp'].month == 3
    assert result['timestamp'].day == 27
    assert result['timestamp'].hour == 12
    assert result['timestamp'].minute == 36
    assert result['timestamp'].second == 45


def test_parse_empty_file(tmp_path):
    """Тест парсинга пустого файла"""
    parser = LogParser()
    empty_file = tmp_path / "empty.log"
    empty_file.write_text("")
    
    result = parser.parse_file(str(empty_file))
    assert result == []


def test_parse_file_with_invalid_lines(tmp_path):
    """Тест парсинга файла с невалидными строками"""
    parser = LogParser()
    log_file = tmp_path / "mixed.log"
    content = """
Invalid line
2025-03-27 12:36:45,000 INFO django.request: GET /api/v1/test/ 200 OK
Another invalid line
2025-03-27 12:36:46,000 ERROR django.request: Error: /api/v1/users/
    """
    log_file.write_text(content.strip())
    
    result = parser.parse_file(str(log_file))
    
    assert len(result) == 2  # Только валидные строки
    assert result[0]['path'] == '/api/v1/test/'
    assert result[1]['path'] == '/api/v1/users/'


def test_parse_malformed_timestamp():
    """Тест парсинга некорректной временной метки"""
    parser = LogParser()
    log_line = '2025-13-45 25:66:99,000 INFO django.request: GET /api/v1/test/ 200 OK'
    
    result = parser._parse_line(log_line)
    assert result is None


def test_extract_path():
    """Тест извлечения пути из разных форматов сообщений"""
    parser = LogParser()
    
    # Тест обычного запроса
    assert parser._extract_path('GET /api/v1/test/ 200 OK') == '/api/v1/test/'
    
    # Тест запроса с ошибкой
    assert parser._extract_path('Error: /api/v1/users/') == '/api/v1/users/'
    
    # Тест невалидного сообщения
    assert parser._extract_path('Invalid message') is None
