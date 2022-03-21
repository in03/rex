#!/usr/bin/env python3.6
from rich import print

# Print CLI title
print("[bold red]REX[/] :t-rex:")

import logging
import subprocess
import webbrowser
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm

from ..settings.manager import SettingsManager
from .utils.core import setup_rich_logging


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
    webbrowser.open_new(settings.user_file)


def init():
    """Run before CLI App load."""
    print("")


def main():
    init()
    cli_app()


if __name__ == "__main__":
    main()
