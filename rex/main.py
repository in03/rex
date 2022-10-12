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

from pydavinci import davinci

rich_tracebacks.install()
settings = SettingsManager()

logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])

resolve = davinci.Resolve()


class Backup:
    def __init__(self):

        self.project = resolve.project
        self.timestamp = datetime.now().strftime("%H%M%S")
        self.backup_filename = f"{self.project.name}_{self.timestamp}.drp"
        static_dir = os.path.normpath(settings["backup"]["static_dir"])
        self.backup_filepath = os.path.join(static_dir, self.backup_filename)

        print(f"Backup Name: {self.backup_filename}")
        print(f"Backup Path: {self.backup_filepath}")

    def run(self, generate_checksum: bool = True, de_duplicate: bool = True):
        """
        Run the backup routine

        Args:
            generate_checksum (bool, optional): Generate an md5 checksum file alongside project backup .drp. Defaults to True.
            de_duplicate (bool, optional): Compare neighbouring checksums and symlink file if they're identical. Defaults to True.
        """

        if not generate_checksum and de_duplicate:
            raise ValueError("generate_checksum must be enabled to de-duplicate!")

        if de_duplicate:
            logger.info("Gathering existing checksums...")
            self.gather_checksums()

        logger.info("Exporting project backup...")
        self.export_project()

        if generate_checksum:
            logger.info("Generating checksum...")
            self.generate_checksum()

        if de_duplicate:
            logger.info("De-duplicating...")
            self.de_duplicate()

    def export_project(self):

        assert resolve.project_manager.export_project(
            project_name=self.project.name,
            path=self.backup_filepath,
            stills_and_luts=True,
        )

    def generate_checksum(self):

        assert os.path.exists(self.backup_filepath)

        def md5sum(file_):
            hash = md5()
            with open(file_, "rb") as f:
                for chunk in iter(lambda: f.read(128 * hash.block_size), b""):
                    hash.update(chunk)
            return hash.hexdigest()

        self.checksum_filepath = self.backup_filepath + ".md5"
        with open(self.checksum_filepath, "x") as checksum_file:
            checksum_file.write(md5sum(self.backup_filepath))

    def gather_checksums(self):
        """
        Get checksums.

        Gathers all checksums that match the project backup series.
        """
        self.backup_filepath = os.path.normpath(self.backup_filepath)
        parent_dir = os.path.dirname(self.backup_filepath)
        self.matching_checksums = glob(f"{parent_dir}/*{self.project.name}*.drp.md5")
        sorted(
            self.matching_checksums,
            key=lambda name: os.path.getmtime(os.path.join(name)),
            reverse=False,
        )

    def de_duplicate(self):

        most_recent_checksums = self.matching_checksums[:3]

        def compare_checksums(x: str, y: str):
            """
            Compare two checksum files.

            Args:
                x (str): First file to compare
                y (str): Second file to compare

            Returns:
                bool: Returns True if they match
            """

            file_x = open(x, "rb")
            file_y = open(y, "rb")

            checksum_x = file_x.read()
            checksum_y = file_y.read()
            logger.debug(f"[magenta]{checksum_x} - {checksum_y}")

            if checksum_x == checksum_y:
                return True

            return False

        matching_checksum = None

        x = self.checksum_filepath
        for y in most_recent_checksums:
            logger.debug(
                f"[magenta]Comparing checksum files: '{os.path.basename(x)}' and '{os.path.basename(y)}'"
            )
            if compare_checksums(x, y):
                matching_checksum = y
                break

        if matching_checksum:
            logger.info(f"Most recent match {matching_checksum}")

    def compare_projects(self):

        text1 = open(file1).read()
        text2 = open(file2).read()
        m = SequenceMatcher(None, text1, text2)
        m.ratio()
