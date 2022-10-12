import hashlib
import logging
import os
from datetime import datetime
from difflib import SequenceMatcher
from glob import glob

from pydavinci import davinci
from rich import print
from rich import traceback as rich_tracebacks

from rex.app.utils.core import md5_checksum
from rex.settings.manager import SettingsManager

rich_tracebacks.install(show_locals=True)
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
            self.generate_checksum_file(self.backup_filepath)

        logger.info("De-duplicate...")
        if self.timeline_is_unique():
            return

    def generate_checksum_file(self, file_):

        md5_file = file_ + ".md5"
        with open(md5_file, "x") as checksum_file:
            checksum_file.write(md5_checksum(file_))

    def checksums_match(self, x: str, y: str):

        with open(x, "rb") as x_file:
            x_hash = x_file.read()
            with open(y, "rb") as y_file:
                y_hash = y_file.read()
                if x_hash == y_hash:
                    return True
                return False

    def export_project(self):

        assert resolve.project_manager.export_project(
            project_name=self.project.name,
            path=self.backup_filepath,
            stills_and_luts=True,
        )

    def generate_timelines_checksum(self):

        timelines = resolve.project.timelines
        project_backup_subfolder = os.path.join(self.static_dir, resolve.project.name)
        os.makedirs(project_backup_subfolder, exist_ok=True)

        checksums = []
        for timeline in timelines:

            logger.debug(f"[magenta]Exporting timeline: '{timeline.name}'")
            fcpxml_file = os.path.join(project_backup_subfolder, timeline.name + ".xml")
            assert timeline.export(fcpxml_file, "FCP_7_XML")

            logger.debug(f"[magenta]Generating fcpxml checksum")
            checksums.append(md5_checksum(fcpxml_file))

        logger.debug(f"[magenta]Generating flattened checksum")
        h = hashlib.new("md5")
        h.update("-".join(checksums).encode())
        h.hexdigest()
        timelines_checksum = h.hexdigest()

        self.timelines_checksum_filepath = self.backup_filepath + "_timelines.md5"
        with open(
            self.backup_filepath + "_timelines.md5", "x"
        ) as timelines_checksum_file:
            timelines_checksum_file.write(timelines_checksum)

    def timeline_is_unique(self):

        self.prior_timelines_checksums = glob(
            f"{self.static_dir}/*{self.project.name}*_timelines.md5"
        )
        self.generate_timelines_checksum()

        for x in self.prior_timelines_checksums:
            if not self.checksums_match(x, self.timelines_checksum_filepath):
                logger.info("[yellow]Timeline changes detected. Keeping backup.")
                return True

        logger.info("[green]All project timelines untouched since last 3 versions.")
        return False

    def gather_project_series(self):
        """
        Get all projects in the project series (all backups matching current project)
        """
        self.backup_filepath = os.path.normpath(self.backup_filepath)
        self.matching_checksums = glob(f"{self.static_dir}/*{self.project.name}*.drp")
        sorted(
            self.matching_checksums,
            key=lambda name: os.path.getmtime(os.path.join(name)),
            reverse=False,
        )

    def de_duplicate(self):

        most_recent_checksums = self.matching_checksums[:3]

        def compare_checksums(x: str, y: str):

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
            if compare_checksums(x, y):
                matching_checksum = y
                break

        if matching_checksum:
            logger.info(f"Most recent match {matching_checksum}")
