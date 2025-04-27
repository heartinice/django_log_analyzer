import re
from datetime import datetime
from typing import Dict, List, Optional


class LogParser:
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
        entries = []
        with open(file_path, 'r') as f:
            for line in f:
                entry = self._parse_line(line.strip())
                if entry:
                    entries.append(entry)
        return entries
    
    def _parse_line(self, line: str) -> Optional[Dict]:
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
            return None
        
        if logger == 'django.request':
            request_match = self.REQUEST_PATTERN.search(message)
            if request_match:
                method, path, status = request_match.groups()
                entry.update({
                    'method': method,
                    'path': path,
                    'status': int(status)
                })
            else:
                error_match = re.search(r'Error: ([^\s]+)', message)
                if error_match:
                    entry['path'] = error_match.group(1)
                    entry['method'] = 'ERROR'  # Добавляем метод для ошибок
        
        return entry
    
    def _extract_path(self, message: str) -> Optional[str]:
        request_match = re.search(r'(?:GET|POST|PUT|DELETE|PATCH) ([^\s]+)', message)
        if request_match:
            return request_match.group(1)
        
        error_match = re.search(r'Error: ([^\s]+)', message)
        if error_match:
            return error_match.group(1)
        
        return None
