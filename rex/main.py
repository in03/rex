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

    def run(self, generate_checksum: bool = True, de_duplicate: bool = True):
        """
        Run the backup routine

        Args:
            generate_checksum (bool, optional): Generate an md5 checksum file alongside project backup .drp. Defaults to True.
            de_duplicate (bool, optional): Compare neighbouring checksums and symlink file if they're identical. Defaults to True.
        """

        if de_duplicate:
            logger.info("Gathering existing checksums...")
            self.gather_project_series()

        logger.info("Exporting project backup...")
        self.export_project()

        if de_duplicate:
            logger.info("De-duplicating...")
            self.de_duplicate()

        if generate_checksum:
            logger.info("Generating checksum...")
            self.generate_checksum()

    def generate_checksum(self):

        hash_md5 = hashlib.md5()
        with open(self.backup_filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        with open(self.backup_filepath + ".md5", "x") as checksum_file:
            checksum_file.write(hash_md5.hexdigest())

    def export_project(self):

        assert resolve.project_manager.export_project(
            project_name=self.project.name,
            path=self.backup_filepath,
            stills_and_luts=True,
        )

    def gather_project_series(self):
        """
        Get all projects in the project series (all backups matching current project)
        """
        self.backup_filepath = os.path.normpath(self.backup_filepath)
        parent_dir = os.path.dirname(self.backup_filepath)
        self.matching_checksums = glob(f"{parent_dir}/*{self.project.name}*.drp")
        sorted(
            self.matching_checksums,
            key=lambda name: os.path.getmtime(os.path.join(name)),
            reverse=False,
        )

    def de_duplicate(self):

        most_recent_checksums = self.matching_checksums[:3]

        def compare_projects(x: str, y: str):

            file_x = open(x, "rb").read()
            file_y = open(y, "rb").read()
            m = SequenceMatcher(None, file_x, file_y)
            ratio = m.quick_ratio()

            logger.debug(f"[magenta]Match ratio is: {ratio}")

            if ratio >= 0.990:
                return True

            return False

        matching_checksum = None

        x = self.backup_filepath
        for y in most_recent_checksums:
            logger.debug(
                f"[magenta]Comparing checksum files: '{os.path.basename(x)}' and '{os.path.basename(y)}'"
            )
            if compare_projects(x, y):
                matching_checksum = y
                break

        if matching_checksum:
            logger.info(f"Most recent match {matching_checksum}")
