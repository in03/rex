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

from pydavinci import davinci

# Init classes
console = Console()
settings = SettingsManager()

cli_app = typer.Typer()

setup_rich_logging()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


@cli_app.command()
def info():
    """
    Get information about the current Resolve environment.

    - Resolve version
    - List of databases
    - Current database
    - Current project
    """
    resolve = davinci.Resolve()
    connected_dbs = resolve.project_manager.db_list

    print(f"[cyan]Resolve version:[/] [magenta]{resolve.version}")

    print("[cyan]Connected databases:")
    for x in connected_dbs:
        print(f" * [magenta]{x['DbName']} - {x['DbType']} - {x['IpAddress']}")
    print()

    print(f"[cyan]Active database:[/] [magenta]{resolve.project_manager.db['DbName']}")

    print(f"[cyan]Active project:[/] [magenta]{resolve.project.name}")
    print(f"[cyan]Active timeline:[/] [magenta]{resolve.active_timeline.name}")


@cli_app.command()
def backup(
    dry_run: bool = typer.Option(
        False, help="Test run the backup command without actually writing files."
    ),
):
    """Backup the current Resolve project to configured path now"""

    print("[green]Backing up projects :inbox_tray:")
    from rex import main

    backup = main.Backup()
    backup.run()


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""

    print("[green]Opening user settings file for modification")
    typer.launch(settings.user_file)


def init():
    """Run before CLI App load."""
    print()


def main():
    init()
    cli_app()


if __name__ == "__main__":
    main()
