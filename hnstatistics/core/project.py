from hnstatistics.core.statistics.model import StatisticsModel


class Project:
    def __init__(self, name: str, project_id: int = None, stats=None):
        self.id = project_id
        self.name = name
        self.stats = stats if stats is not None else StatisticsModel()