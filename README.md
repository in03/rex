# REX

![Rex logo](https://github.com/in03/rex/blob/main/docs/images/rex_logo.svg)
![GitHub](https://img.shields.io/github/license/in03/rex) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub branch checks state](https://img.shields.io/github/checks-status/in03/rex/main)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/in03/rex/main.svg)](https://results.pre-commit.ci/latest/github/in03/rex/main)

![GitHub last commit](https://img.shields.io/github/last-commit/in03/rex)
![GitHub Repo stars](https://img.shields.io/github/stars/in03/rex?style=social)

---

##### Avoid extinction-level events with your DaVinci Resolve projects :sparkles:
Rex makes backing up, verifying and restoring individual project files an Endeavour of Minimal Fuss .
Wrestle no longer with manually export projects, missing automatic-backups or temporarily restoring databases for a single project.
Rex schedules flexible, de-duplicated project backups when you're at your least busy; and automatically uploads them to your own cloud-storage. 

> **Note**
>
> Currently only Resolve 18 is supported. Resolve 17 and older require Python 3.6, which is now EOL. Some dependencies have started dropping support for it. 
> A Resolve 17 branch doesn't currently exist, and will not unless someone asks nicely for it or forks the project.

## Why?

DaVinci Resolve stores all of its projects in a database (PostgreSQL), not individual project files. And while databases are awesome for many reasons, they do come with some downsides. A centralised database of projects is convenient on a good day and costly on a bad one. Should the database server go down, you lose access to all your projects. You can mitigate this with database backups, but database backups can be complicated to restore. Restoring a database due to data-loss, corruption, human-error, etc, can be very time consuming. If it's a production database, downtime can be particularly costly.

Take my aforementioned "project roll-back" scenario from above, but lets spice it up a bit. Imagine you've found that an entire timeline has been deleted and has actually been missing for a while. In fact you don't know how long it's been missing for. Without a project backup you'll have to restore a database backup. Potentially the steps for that can look like this:

1. Find a free system that can host a temporary database (you can't use the same one without incurring downtime: Resolve only connects to port 5432)
2. Take a guess at how long the timeline has been missing and restore a database backup a few days older than the first backup.
3. Yay! You found the timeline, but not all the changes are there. Maybe. Restore another database backup just to check.
4. Perfect! Found it. Alright, export a DaVinci Resolve timeline file.
5. Stop (and maybe remove) the temporary database server.
6. Import the exported timeline into the current project.

Second try might be pretty lucky if it's a long running project.
Therein lies one of the main benefits of running Rex. If you have project backups running alongside database backups, you can much more easily roll-back a single project.

## How does it work?
Run `rex up` and Rex runs as a background process using a given schedule to trigger actions.
When a scheduled backup event is reached, Rex waits until you're at your least busy, then exports a DaVinci Resolve project file.
That DRP is then hashed and compared to existing DRPs. If they match, the duplicate is discared to save space and a symlink is used in place.
if you've setup a cloud-backup service with Rex, if the new DRP file matches the upload criteria (you can set filters so you're not backing up every single DRP in cloud), it will be uploaded.

Once in a while all the projects are rehashed and compared to their old hashes. If they don't match, Rex will warn you and prompt you to overwrite it with a version backed up in cloud.

> **Note**
>
> Rex navigates projects in your database using Resolve's Python API. There's no UI automation, keylogging or phoning home - other than anything you set up 
> yourself with the cloud storage integrations. I'd encourage you to check the source code to be sure. Never trust strange software. 

## Installation
Install the latest version of Python. You can use official installers or pyenv. Add it to path.
Since Rex is a CLI application, install it with pipx.

```
pipx install git+https://github.com/in03/rex

# OR

pipx install git+https://github.com/in03/rex@resolve-17
```

## Why 'Rex'?
CLI entrypoints are like domain names. You want them short, memorable and it's nice if you can type them with one hand.
`Rex` fits the bill I'm sorting going for a space theme with my projects at the moment. It's also kind of an awkward acronym derived from **R**esolve Project **EX**porter.
