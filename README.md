# Resolve Export Projects
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/in03/resolve-project-exporter/main.svg)](https://results.pre-commit.ci/latest/github/in03/resolve-project-exporter/main) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 ---
NOTE!: Still a work in progress, not everything is implemented.
 
## What's it for? ##
DaVinci Resolve stores all of its projects in a database, not individual project files.
This comes with a lot of benefits, but physical files on disk bring a good deal of peace of mind.
There's currently no easy way to batch export all projects in a database as project files, this aims to fill that gap.
 
## How does it work? ##
It literally just batches through all projects in the database using Resolve's API.
There are some settings defined in `user_settings.yml` that allow for customisation.

## What does it need?
**This app has a few non-negotiable prerequisites:**
- Python 3.6 **ONLY** (DaVinci Resolve's Python API requires it)
- DaVinci Resolve Studio, with scripting set up (read Resolve's scripting README)

## How do I install it?
### A Warning about Python 3.6

Because DaVinci Resolve requires Python 3.6 to communicate with it's API, no versions over Python 3.6 will work with REX.
Unfortunately this means that REX may get stuck using older versions of certain packages as they begin to drop support for 3.6.
It also means that security patches for some dependencies won't make it into REX
This kind of setup almost guarantees dependency conflicts if you have multiple Python CLI tools you keep installed.
To mitigate this you can:

- Use Python 3.6 for REX **ONLY** and install a newer Python alongside for your other needs.

- Install a tool like *pipx* that isolates Python CLI tools with their own virtual environments but keeps them on path.


## Configuration
On first run, you'll be prompted to alter your settings. The app will copy the default settings to the OS user configuration folder. 
- **Linux/Mac:** `$XDG_HOME_CONFIG/resolve_proxy_encoder/user_settings.yml`
- **Windows:** `%homepath%/resolve_proxy_encoder/user_settings.yml`


## How can I contribute?
Clone the repo, install dependencies, call from poetry shell:
```
git clone https://github.com/in03/resolve-export-projects
cd resolve-export-projects
py -3.6 -m pip install poetry
py -3.6 -m poetry shell
poetry install
rprox
```
If you're unfamiliar with using Poetry for dependency management and packaging, [give it a look](https://python-poetry.org/docs/basic-usage).

## How do I use it?

```
Usage: rex [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  backup Batch export all projects in the current Resolve DB...
  ```
