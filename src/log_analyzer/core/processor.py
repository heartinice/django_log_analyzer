import multiprocessing
from typing import Dict, List
from .parser import LogParser


class LogProcessor:
    """
    Класс для обработки лог-файлов.
    Поддерживает параллельную обработку нескольких файлов.
    """
    
    def __init__(self, log_files: List[str]):
        self.log_files = log_files
        self.parser = LogParser()

    def process_files(self) -> List[Dict]:
        """
        Обрабатывает все файлы логов параллельно.
        
        Returns:
            List[Dict]: Список обработанных записей логов
        """
        with multiprocessing.Pool() as pool:
            results = pool.map(self.parser.parse_file, self.log_files)
        
        all_entries = []
        for result in results:
            all_entries.extend(result)
        
        return all_entries
