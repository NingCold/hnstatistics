from hnstatistics.core.statistics.algorithms import calculate_probability, count_frequencies
from hnstatistics.core.errors import ProjectEmptyError
from hnstatistics.core.statistics.analyze_options import AnalyzeOptions

class StatisticsModel:
    def __init__(self):
        self.frequency = {}
        self.probability = {}
    
    def merge(self, new_freq: dict):
        if not new_freq:
            raise ProjectEmptyError()
        for k, v in new_freq.items():
            self.frequency[k] = self.frequency.get(k, 0) + v
        self._recalc()
    
    def overwrite(self, new_freq: dict):
        if not new_freq:
            raise ProjectEmptyError()
        self.frequency = new_freq
        self._recalc()
        
    def analyze(self, text: str, options: AnalyzeOptions):
        self.frequency = count_frequencies(text, options)
        self.probability = calculate_probability(self.frequency)
    
    def _recalc(self):
        total = sum(self.frequency.values())
        self.probability = {
            k: v / total for k, v in self.frequency.items()
        }