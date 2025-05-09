# src/log_analyzer/reports/handlers.py
from collections import defaultdict
from typing import Dict, List
from .base import BaseReport


class HandlersReport(BaseReport):
    LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def generate(self, log_data: List[Dict]) -> None:
        stats = self._aggregate_stats(log_data)
        self._print_report(stats)

    def _aggregate_stats(self, log_data: List[Dict]) -> Dict:
        stats = defaultdict(lambda: {level: 0 for level in self.LOG_LEVELS})
        total_requests = 0
        
        for entry in log_data:
            if entry.get("logger") == "django.request" and entry.get("path"):
                handler = entry["path"]
                level = entry["level"]
                stats[handler][level] += 1
                total_requests += 1
        
        return {
            "stats": dict(stats),
            "total": total_requests
        }

    def _print_report(self, stats: Dict) -> None:
        print(f"\nTotal requests: {stats['total']}\n")
        
        print(f"{'HANDLER':<20}\t", end="")
        for level in self.LOG_LEVELS:
            print(f"{level:<8}\t", end="")
        print()
        
        handlers = sorted(stats["stats"].keys())  
        level_totals = defaultdict(int)
        
        for handler in handlers:  
            print(f"{handler:<20}\t", end="")
            for level in self.LOG_LEVELS:
                count = stats["stats"][handler].get(level, 0)
                level_totals[level] += count
                print(f"{count:<8}\t", end="")
            print()
        
        print(f"{'':<20}\t", end="")
        for level in self.LOG_LEVELS:
            print(f"{level_totals[level]:<8}\t", end="")
        print()