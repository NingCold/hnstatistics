from copy import deepcopy
from hnstatistics.core.project import Project
from hnstatistics.core.statistics.commit_mode import CommitMode
from hnstatistics.core.statistics.draft import DraftStatistics
from hnstatistics.core.statistics.model import StatisticsModel
from hnstatistics.core.uow import UnitOfWork


class StatisticsService:
    def create_draft(self):
        return DraftStatistics()

    def analyze_draft(self, draft: DraftStatistics, text: str):
        draft.snapshot()
        draft.current.analyze(text)

    def merge_draft(self, draft: DraftStatistics, new_stats: StatisticsModel):
        draft.snapshot()
        draft.current.merge(new_stats.frequency)

    def overwrite_draft(self, draft: DraftStatistics, new_stats: StatisticsModel):
        draft.snapshot()
        draft.current.overwrite(new_stats.frequency)

    def commit(self, project: Project, stats: StatisticsModel, mode: CommitMode):
        if not stats:
            raise ValueError("No statistics to commit.")
        
        if mode == CommitMode.MERGE:
            project.stats.merge(stats.frequency)
        elif mode == CommitMode.OVERWRITE:
            project.stats = deepcopy(stats)
        else:
            raise ValueError(f"Unsupported commit mode: {mode}")

        with UnitOfWork() as uow:
            uow.statistics.update(project.id, project.stats)
            uow.commit()
    
    def merge_statistics(self, base_stats: StatisticsModel, new_stats: StatisticsModel):
        base_stats.merge(new_stats.frequency)
    
    def overwrite_statistics(self, base_stats: StatisticsModel, new_stats: StatisticsModel):
        base_stats.overwrite(new_stats.frequency)
    
    def analyze_text(self, text: str) -> StatisticsModel:
        stats = StatisticsModel()
        stats.analyze(text)
        return stats