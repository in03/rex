import logging
import os
from datetime import datetime
from rich import print
from rich import traceback as rich_tracebacks

from rex.app.utils import core
from rex.settings.manager import SettingsManager
from yaspin import yaspin

from pydavinci import davinci

rich_tracebacks.install()
settings = SettingsManager()
logger = logging.getLogger(__name__)

resolve = davinci.Resolve()


@yaspin(text="Backing up...")
def backup():

    active_project_name = resolve.project.name
    timestamp = datetime.now().strftime("%H%M%S")
    backup_filename = (
        f"{resolve.project.name}_{resolve.active_timeline.name}_{timestamp}.drp"
    )
    backup_path = os.path.join(settings["backup"]["static_dir"], backup_filename)

    assert resolve.project_manager.export_project(
        project_name=active_project_name,
        path=backup_path,
        stills_and_luts=True,
    )
