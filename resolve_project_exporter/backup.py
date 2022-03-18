import imp
import logging
import sys

from rich import print

from .app.utils import core
from .settings.manager import SettingsManager

settings = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app", "loglevel"])

from yaspin import yaspin


class ResolveObjects:
    def __init__(self):
        self._populate_variables()

    def _get_resolve(self):

        ext = ".so"
        if sys.platform.startswith("darwin"):
            path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\"
            ext = ".dll"
        elif sys.platform.startswith("linux"):
            path = "/opt/resolve/libs/Fusion/"
        else:
            raise Exception("Unsupported system! " + sys.platform)

        bmd = imp.load_dynamic("fusionscript", path + "fusionscript" + ext)
        resolve = bmd.scriptapp("Resolve")

        if not resolve:
            return None

        try:
            sys.modules[__name__] = resolve
        except ImportError:
            return None

        return resolve

    def _populate_variables(self):

        try:

            self.resolve = self._get_resolve()
            if self.resolve is None:
                raise TypeError

        except:

            logger.warning(
                "[red] :warning: Couldn't access the Resolve Python API. Is DaVinci Resolve running?[/]"
            )
            core.app_exit(1, -1)

        try:

            self.project_manager = self.resolve.GetProjectManager()
            if self.project_manager is None:
                raise TypeError

        except:

            logger.warning(
                "[red] :warning: Couldn't get Resolve API. Is resolve running?[/]"
            )
            core.app_exit(1, -1)


def main():

    r_ = ResolveObjects()

    # Print DB info
    current_db = r_.project_manager.GetCurrentDatabase()
    print(
        "[bold cyan]DB:[/] [green]"
        + " - ".join([v for v in current_db.values()])
        + "[/]"
    )

    # TODO: Iterate first for a count of projects, then use for a progress bar when exporting
    # labels: enhancement

    # Iterate all projects
    projects = []
    spinner = yaspin(text="Iterating projects...")
    if logger.getEffectiveLevel() >= 30:  # Warn or above
        spinner.start()

    # in root folder
    logger.debug(f"[cyan]Projects in root:[/]\n")
    r_.project_manager.GotoRootFolder()
    project_list = sorted(r_.project_manager.GetProjectListInCurrentFolder())
    for project in project_list:
        spinner.text = f'Exporting "{project}"...'
        # TODO: Add a dryrun option
        # labels: enhancement
        # r_.project_manager.ExportProject(project, output_path, withStillsAndLUTs=True)

    logger.debug(project_list)
    projects.extend(project_list)

    # in subfolders
    subfolders = r_.project_manager.GetFolderListInCurrentFolder()
    for subfolder in subfolders:

        def recurse_subfolder(subfolder):
            projects_in_root = True
            logger.debug(f'[cyan bold]"{subfolder}":')

            if r_.project_manager.OpenFolder(subfolder):

                project_list = sorted(
                    r_.project_manager.GetProjectListInCurrentFolder()
                )
                if project_list:

                    logger.debug("[cyan]Found projects:[/]")
                    logger.debug(project_list)
                    for project in project_list:

                        output_path = settings["export", "archive_static_dir"]
                        spinner.text = f'Exporting "{project}"...'
                        # r_.project_manager.ExportProject(project, output_path, withStillsAndLUTs=True)

                    projects.extend(project_list)

                else:
                    logger.debug("[yellow]No projects in folder root.[/]")
                    projects_in_root = False

                more_folders = r_.project_manager.GetFolderListInCurrentFolder()
                if more_folders:
                    logger.debug(f"[cyan]Found folders:[/]\n{more_folders}")
                    for more_folder in more_folders:
                        logger.debug("")
                        recurse_subfolder(more_folder)
                else:
                    dead_end_folder = r_.project_manager.GetCurrentFolder()
                    if not projects_in_root:
                        logger.debug(f"[red bold]EMPTY. Should delete!")
                    else:
                        logger.debug(f'[cyan]No more in: "{dead_end_folder}"')

            # Leave once done and no more to recurse
            logger.debug(":point_up: Back up one dir\n")
            r_.project_manager.GotoParentFolder()

            # Back to root, since navigating actual Resolve UI
            # (Leave it nice and tidy ;) )
            r_.project_manager.GotoRootFolder()

        recurse_subfolder(subfolder)

    spinner.stop()
    logger.debug(projects)
    logger.info(f"[cyan]Total Projects:[/] {len(projects)}")


if __name__ == "__main__":
    main()
