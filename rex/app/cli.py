#!/usr/bin/env python3.6

import sys
from pyfiglet import Figlet
from rich import print

fig = Figlet()

sys.stdout.write(fig.renderText("rex"))
print("[bold]R[/bold]esolve project [bold]Ex[/bold]porter")
print("[bold]Schedule and manage DaVinci Resolve project backups :t-rex:\n")


import logging

import typer
from rich.console import Console

from rex.settings.manager import SettingsManager
from rex.app.utils.core import setup_rich_logging


# Init classes
console = Console()
settings = SettingsManager()

cli_app = typer.Typer()

setup_rich_logging()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


@cli_app.command()
def backup(
    dry_run: bool = typer.Option(
        False, help="Test run the backup command without actually writing files."
    ),
    active_only: bool = typer.Option(
        settings["backup", "active_only"],
        help="Only backup the project that is currently open in Resolve.",
    ),
):
    """Backup projects in the DaVinci Resolve database as DaVinci Resolve project files"""

    print("[green]Backing up projects :inbox_tray:")
    from .. import backup

    if active_only:
        logger.warning("[bold red]Backup active only not yet implemented.")
    else:
        backup.batch_backup(dry_run=dry_run)


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""

    print("[green]Opening user settings file for modification")
    typer.launch(settings.user_file)


def init():
    """Run before CLI App load."""
    print("")


def main():
    init()
    cli_app()


if __name__ == "__main__":
    main()
