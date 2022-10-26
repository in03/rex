from fastapi import FastAPI
from pydavinci import davinci
from rex.app.main import Backup


app = FastAPI()
resolve = davinci.Resolve()


@app.get("/")
async def welcome():
    return {"Greeting": "Welcome to Rex REST API! - check out docs @ '/docs'"}


@app.get("/resolve_version")
async def get_resolve_version() -> str:
    return resolve.version


@app.get("/databases")
async def get_databases() -> list[dict[str, str]]:
    return resolve.project_manager.db_list


@app.get("/current_database")
async def current_database() -> dict[str, str]:
    return resolve.project_manager.db


@app.get("/projects")
async def all_projects() -> list[str]:
    """
    A list of all project names in current project manager folder

    Returns:
        list[str]: project names
    """
    return resolve.project_manager.projects


@app.get("/current_project")
async def current_project_info() -> str:
    return resolve.project.name


@app.get("/backup")
async def backup_current_project() -> bool:
    """
    Backup the active Resolve project now

    Returns:
        bool: ``True`` if successful, ``False`` otherwise
    """
    backup = Backup()
    if not backup.run():
        return False
    return True
