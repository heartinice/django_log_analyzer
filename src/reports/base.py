from abc import ABC, abstractmethod
from typing import Dict, List


class BaseReport(ABC):
    @abstractmethod
    def generate(self, log_data: List[Dict]) -> None:
        pass
