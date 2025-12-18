from copy import deepcopy
from hnstatistics.core.statistics.model import StatisticsModel


class DraftStatistics:
    def __init__(self):
        self._history = []
        self._future = []
        self.current = StatisticsModel()

    def snapshot(self):
        self._history.append(deepcopy(self.current))
        self._future.clear()

    def undo(self):
        if not self._history:
            return
        self._future.append(self.current)
        self.current = self._history.pop()

    def redo(self):
        if not self._future:
            return
        self._history.append(self.current)
        self.current = self._future.pop()
