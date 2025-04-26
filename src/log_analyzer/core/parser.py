import re
from datetime import datetime
from typing import Dict, List, Optional


class LogParser:
    """
    Парсер лог-файлов Django.
    """
    
    LOG_PATTERN = re.compile(
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) '
        r'(\w+) '
        r'([\w.]+): '
        r'(.+)'
    )
    
    REQUEST_PATTERN = re.compile(
        r'(GET|POST|PUT|DELETE|PATCH) ([^\s]+) (\d{3})'
    )
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        Парсит файл лога и возвращает список записей.
        
        Args:
            file_path: Путь к файлу лога
        
        Returns:
            List[Dict]: Список обработанных записей логов
        """
        entries = []
        with open(file_path, 'r') as f:
            for line in f:
                entry = self._parse_line(line.strip())
                if entry:
                    entries.append(entry)
        return entries
    
    def _parse_line(self, line: str) -> Optional[Dict]:
        """
        Парсит одну строку лога.
        
        Args:
            line: Строка лога
        
        Returns:
            Dict: Словарь с данными из лога или None, если строка не распознана
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        timestamp_str, level, logger, message = match.groups()
        
        try:
            entry = {
                'timestamp': datetime.strptime(
                    timestamp_str,
                    '%Y-%m-%d %H:%M:%S,%f'
                ),
                'level': level,
                'logger': logger,
                'message': message
            }
        except ValueError:
            # Если не удалось распарсить дату
            return None
        
        if logger == 'django.request':
            # Для обычных запросов
            request_match = self.REQUEST_PATTERN.search(message)
            if request_match:
                method, path, status = request_match.groups()
                entry.update({
                    'method': method,
                    'path': path,
                    'status': int(status)
                })
            else:
                # Для сообщений об ошибках
                error_match = re.search(r'Error: ([^\s]+)', message)
                if error_match:
                    entry['path'] = error_match.group(1)
                    entry['method'] = 'ERROR'  # Добавляем метод для ошибок
        
        return entry
    
    def _extract_path(self, message: str) -> Optional[str]:
        """
        Извлекает путь из сообщения лога.
        """
        # Для обычных запросов
        request_match = re.search(r'(?:GET|POST|PUT|DELETE|PATCH) ([^\s]+)', message)
        if request_match:
            return request_match.group(1)
        
        # Для сообщений об ошибках
        error_match = re.search(r'Error: ([^\s]+)', message)
        if error_match:
            return error_match.group(1)
        
        return None
