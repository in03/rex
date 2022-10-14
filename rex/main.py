import logging
import os
from datetime import datetime
from rich import print
from rich import traceback as rich_tracebacks

from rex.app.utils import core
from rex.settings.manager import SettingsManager
from rex import exceptions
from yaspin import yaspin
from glob import glob
from difflib import SequenceMatcher
import hashlib
from pydavinci import davinci

rich_tracebacks.install()
settings = SettingsManager()

logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])

resolve = davinci.Resolve()


class Backup:
    def __init__(self):

        # TODO: Ensure no wrongful file collisions
        # Use database name, type, ip address, and project path/folder structure in project manager
        # to create a unique hash for the backup name. Keep the timestamp. So backups are still unique.

        self.project = resolve.project
        self.db_name = resolve.project_manager.db["DbName"]
        self.timestamp = datetime.now().strftime("%H%M%S")

        self.backup_filename = (
            f"{self.db_name}_{self.project.name}_{self.timestamp}.drp"
        )
        self.static_dir = os.path.normpath(settings["backup"]["static_dir"])
        self.backup_filepath = os.path.join(self.static_dir, self.backup_filename)

        print(f"Backup Name: '{self.backup_filename}'")
        print(f"Backup Path: '{self.static_dir}'")

    def run(self, generate_checksum: bool = True) -> bool:
        """
        Run the backup routine

        Args:
            generate_checksum (bool, optional): Generate an md5 checksum file alongside project backup .drp. Defaults to True.
        """

        logger.info("Exporting project backup...")
        if not self.export_project():
            return False

        if generate_checksum:
            logger.info("Generating checksum...")
            if not self.generate_checksum():
                return False

        return True

    def export_project(self) -> bool:
        return resolve.project_manager.export_project(
            project_name=self.project.name,
            path=self.backup_filepath,
            stills_and_luts=True,
        )

    def generate_checksum(self) -> bool:
        try:
            hash_md5 = hashlib.md5()
            with open(self.backup_filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)

            with open(self.backup_filepath + ".md5", "x") as checksum_file:
                checksum_file.write(hash_md5.hexdigest())

            return True

        except Exception as e:
            logger.error(e)
            return False
