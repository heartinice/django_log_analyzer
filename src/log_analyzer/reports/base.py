from abc import ABC, abstractmethod
from typing import Dict, List


class BaseReport(ABC):
    """
    Базовый класс для всех отчетов.
    Определяет интерфейс, который должны реализовать все отчеты.
    """
    
    @abstractmethod
    def generate(self, log_data: List[Dict]) -> None:
        """
        Генерирует отчет на основе обработанных данных логов.
        
        Args:
            log_data: Список словарей с данными из логов
        """
        pass
