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
def backup():
    """
    Backup projects in active DaVinci Resolve database
    """

    print("\n\n[green]Backing up projects[/] :outbox_tray:")
    from .. import backup

    backup.main()


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""

    print("[green]Opening user settings file for modification")
    webbrowser.open_new(settings.user_file)


def init():
    """Run before CLI App load."""
    print("YAYA DINGDONG")


def main():
    init()
    cli_app()


if __name__ == "__main__":
    main()
