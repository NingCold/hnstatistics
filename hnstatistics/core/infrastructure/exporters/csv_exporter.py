import csv

from hnstatistics.core.errors import ExportIOError, ExportPathError, ProjectEmptyError
from hnstatistics.core.statistics.model import StatisticsModel

def export_csv(stats: StatisticsModel, file_path: str):
    if not stats or not stats.frequency:
        raise ProjectEmptyError()
    
    if not file_path or not isinstance(file_path, str):
        raise ExportPathError(file_path, "Export file path is invalid.")
    
    try:
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Item", "Frequency", "Probability"])

            for k in stats.frequency:
                writer.writerow([
                    k,
                    stats.frequency[k],
                    round(stats.probability.get(k, 0), 4)
                ])
    except OSError as e:
        raise ExportIOError(file_path, str(e))