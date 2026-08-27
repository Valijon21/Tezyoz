"""
Typing metrics calculation modules for TypeMaster.
"""
from typing import List

class WpmCalculator:
    @staticmethod
    def calculate(correct_characters: int, elapsed_time_seconds: float) -> float:
        """
        Calculates Net Words Per Minute.
        Net WPM = (correct_characters / 5.0) / (elapsed_time_seconds / 60.0)
        """
        elapsed_minutes = elapsed_time_seconds / 60.0
        if elapsed_minutes <= 0.0:
            return 0.0
        return (correct_characters / 5.0) / elapsed_minutes


class RawWpmCalculator:
    @staticmethod
    def calculate(total_typed_characters: int, elapsed_time_seconds: float) -> float:
        """
        Calculates Raw Words Per Minute inclusive of errors.
        Raw WPM = (total_typed_characters / 5.0) / (elapsed_time_seconds / 60.0)
        """
        elapsed_minutes = elapsed_time_seconds / 60.0
        if elapsed_minutes <= 0.0:
            return 0.0
        return (total_typed_characters / 5.0) / elapsed_minutes


class AccuracyCalculator:
    @staticmethod
    def calculate(correct_characters: int, total_typed_characters: int) -> float:
        """
        Calculates typing accuracy percentage.
        Accuracy = (correct_characters / total_typed_characters) * 100.0
        """
        if total_typed_characters <= 0:
            return 0.0
        return (correct_characters / total_typed_characters) * 100.0


class ConsistencyCalculator:
    @staticmethod
    def calculate(keystroke_times: List[float]) -> float:
        """
        Calculates consistency of typing pace.
        Calculated based on standard deviation of inter-key intervals (latencies).
        Consistency = max(0.0, (1.0 - Standard_Deviation / Mean) * 100.0)
        """
        if len(keystroke_times) < 3:
            return 100.0

        intervals = []
        for i in range(1, len(keystroke_times)):
            intervals.append(keystroke_times[i] - keystroke_times[i-1])

        n = len(intervals)
        mean = sum(intervals) / n
        if mean == 0.0:
            return 0.0

        variance = sum((x - mean) ** 2 for x in intervals) / n
        std_dev = variance ** 0.5

        cv = std_dev / mean
        consistency = max(0.0, (1.0 - cv) * 100.0)
        return consistency
