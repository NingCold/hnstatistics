from hnstatistics.core.errors import ProjectNotSelectedError
from hnstatistics.core.project import Project
from hnstatistics.core.repositories.sqlite_project_repo import SQLiteProjectRepository
from hnstatistics.core.uow import UnitOfWork


class ProjectService:
    def list_projects(self) -> list[Project]:
        with UnitOfWork() as uow:
            return uow.projects.get_all()
    
    def create(self, name: str) -> Project:
        with UnitOfWork() as uow:
            project_id = uow.projects.insert(name)
            return Project(name=name, project_id=project_id)
    
    def rename(self, project_id: int, new_name: str):
        with UnitOfWork() as uow:
            uow.projects.rename(project_id, new_name)
    
    def delete(self, project_id: int):
        with UnitOfWork() as uow:
            uow.projects.delete(project_id)
    
    def load(self, project_id: int) -> Project:
        with UnitOfWork() as uow:
            project = uow.projects.get_by_id(project_id)
            statistics  = uow.statistics.get_by_project_id(project_id)
            if project is None:
                raise ProjectNotSelectedError("Project with the given ID does not exist.")
            project.stats = statistics
            return project
    
    def save(self, project: Project):
        with UnitOfWork() as uow:
            uow.projects.update(project)
    
    def save_as(self, project_id: int, new_name: str) -> Project:
        with UnitOfWork() as uow:
            new_project_id = uow.projects.save_as(project_id, new_name)
            return uow.projects.get_by_id(new_project_id)