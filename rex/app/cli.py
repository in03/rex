#!/usr/bin/env python3.6

import sys
from pyfiglet import Figlet
from rich import print

import requests

fig = Figlet()

sys.stdout.write(fig.renderText("rex"))
print("[bold]R[/bold]esolve project [bold]Ex[/bold]porter")
print("[bold]Schedule and manage DaVinci Resolve project backups :t-rex:\n")


import logging

import typer
from rich.console import Console
from rich.panel import Panel

from rex.settings.manager import SettingsManager
from rex.app.utils.core import setup_rich_logging
from requests import ConnectionError, ConnectTimeout
from pydavinci.wrappers.project import Project
from pydavinci import davinci

# Init classes
console = Console()
settings = SettingsManager()

cli_app = typer.Typer()

setup_rich_logging()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])

tld = f"http://{settings['server']['ip']}:{settings['server']['port']}"


@cli_app.command()
def info():
    """
    Get information about the current Resolve environment.

    - Resolve version
    - List of databases
    - Current database
    - Current project
    """

    resolve_version = requests.get(f"{tld}/resolve_version").json()
    databases = requests.get(f"{tld}/databases").json()
    current_db = requests.get(f"{tld}/current_database").json()
    all_projects = requests.get(f"{tld}/projects").json()
    current_project = requests.get(f"{tld}/current_project").json()

    db_print = str()
    for x in databases:
        db_print += f"* {x['DbName']} - {x['DbType']} - {x['IpAddress']}\n"

    info_msg = (
        "\n[magenta bold]RESOLVE VERSION[/]\n"
        f"{resolve_version}\n\n"
        "[magenta bold]AVAILABLE DATABASES[/]\n"
        f"{db_print}\n"
        "[magenta bold]ACTIVE DATABASE[/]\n"
        f"{current_db['DbName']}\n\n"
        "[magenta bold]TOTAL PROJECTS[/]\n"
        f"{len(all_projects)}\n\n"
        f"[magenta bold]ACTIVE PROJECT[/]\n"
        f"{current_project}"
    )

    print(Panel(info_msg, title="[cyan]ENVIRONMENT INFO.", title_align="left"))


@cli_app.command()
def backup(
    dry_run: bool = typer.Option(
        False, help="Test run the backup command without actually writing files."
    ),
):
    """Backup the current Resolve project to configured path now"""

    print("[green]Backing up projects :inbox_tray:")
    from rex import main

    success = requests.get(f"{tld}/backup", timeout=20).json()
    if not success:
        logger.error("[red]Back up failed...")
        return False

    logger.info("[green]Succesfully backed up!")
    return True


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""

    print("[green]Opening user settings file for modification")
    typer.launch(settings.user_file)


def init():
    """Run before CLI App load."""
    print()


def main():
    try:
        init()
        cli_app()
    except ConnectionError:
        ip = settings["server"]["ip"]
        port = settings["server"]["port"]
        logger.error(
            "[magenta]"
            f"Could not connect to Rex server [{ip}:{port}]\n"
            f"Is it definitely running?"
        )


if __name__ == "__main__":
    main()
