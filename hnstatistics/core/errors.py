class HNStatisticsError(Exception):
    """所有业务异常的基类"""
    pass

class RepositoryError(HNStatisticsError):
    """Repository 层通用异常"""
    pass

class DatabaseConnectionError(RepositoryError):
    """数据库连接异常"""
    pass

class TransactionError(RepositoryError):
    """数据库事务异常"""
    pass

class NotFoundError(RepositoryError):
    """未找到数据异常"""
    pass

class DuplicateError(RepositoryError):
    """数据重复异常"""
    pass

class ProjectError(HNStatisticsError):
    """Base class for project-related exceptions."""
    pass

class ProjectNotSelectedError(ProjectError):
    """Exception raised when no project is selected."""
    def __init__(self, message="No project selected. Please select a project first."):
        self.message = message
        super().__init__(self.message)

class ProjectNotLoadedError(ProjectError):
    """Exception raised when a project is not loaded."""
    def __init__(self, message="Project not loaded. Please load a project first."):
        self.message = message
        super().__init__(self.message)

class ProjectEmptyError(ProjectError):
    """Exception raised when the selected project is empty."""
    def __init__(self, message="The selected project is empty. Please add data to the project."):
        self.message = message
        super().__init__(self.message)

class ExportError(HNStatisticsError):
    pass

class ExportPathError(ExportError):
    """Exception raised for errors in the export file path."""
    def __init__(self, path, message="Invalid export file path."):
        self.path = path
        self.message = f"{message} Path: {self.path}"
        super().__init__(self.message)

class ExportIOError(ExportError):
    """Exception raised for I/O errors during export."""
    def __init__(self, path, message="I/O error occurred during export."):
        self.path = path
        self.message = f"{message} Path: {self.path}"
        super().__init__(self.message)

class ExportFormatError(ExportError):
    """Exception raised for unsupported export formats."""
    def __init__(self, format, message="Unsupported export format."):
        self.format = format
        self.message = f"{message} Format: {self.format}"
        super().__init__(self.message)

class DatabaseError(HNStatisticsError):
    """Base class for database-related exceptions."""
    pass

class DatabaseConnectionError(DatabaseError):
    pass


class DatabaseWriteError(DatabaseError):
    pass


class DatabaseReadError(DatabaseError):
    pass