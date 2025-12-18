import json
from hnstatistics.core.errors import ExportIOError, ExportPathError, ProjectEmptyError
from hnstatistics.core.statistics.model import StatisticsModel

def export_json(stats: StatisticsModel, file_path: str):
    if not stats.frequency:
        raise ProjectEmptyError()
    
    if not file_path or not isinstance(file_path, str):
        raise ExportPathError(file_path, "Export file path is invalid.")
    
    data = {
        "statistics": [
            {
                "Item": key,
                "Frequency": stats.frequency[key],
                "Probability": round(stats.probability[key], 4)
            }
            for key in stats.frequency
        ]
    }

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        raise ExportIOError(file_path, str(e))