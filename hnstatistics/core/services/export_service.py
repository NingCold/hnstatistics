from hnstatistics.core.errors import ExportFormatError, ProjectEmptyError
from hnstatistics.core.infrastructure.exporters.csv_exporter import export_csv
from hnstatistics.core.infrastructure.exporters.excel_exporter import export_excel
from hnstatistics.core.infrastructure.exporters.json_exporter import export_json

def export_project(project, file_path: str, fmt: str):
    if project is None:
        raise ProjectEmptyError()
    
    stats = project.stats
    if stats is None or not stats.frequency or not stats.probability:
        raise ProjectEmptyError()
    
    fmt = fmt.lower()
    
    if fmt == "csv":
        export_csv(stats, file_path)
    elif fmt in ("xlsx", "xls"):
        export_excel(stats, file_path)
    elif fmt == "json":
        export_json(stats, file_path)
    else:
        raise ExportFormatError(fmt, "Unsupported export format.")