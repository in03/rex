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

## Project vision
Rex aims to make backing up, verifying and restoring individual project files an *Endeavour of Minimal Fuss* .
Wrestle no longer with manually exported projects, missing automatic-backups or temporarily restoring databases for a single project.
Rex schedules flexible, de-duplicated project backups when you're at your least busy and automatically uploads them to your own cloud-storage. 

## Why?
DaVinci Resolve stores all of its projects in a database (PostgreSQL), not individual project files. And while databases are awesome for many reasons, they do come with some downsides. A centralised database of projects is convenient on a good day and costly on a bad one. Should the database server go down, you lose access to all your projects. You can mitigate this with database backups, and you should! (I recommend [docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local)) But database backups can be complicated to restore: Restoring a database due to data-loss, corruption, human-error, etc, can be very time consuming. If it's just to rescue a single project, it's a lot of overhead. If it's a production database, downtime can be particularly costly. Resolve also doesn't allow connecting to a database with a different port, meaning you need to find a different system to host the database backup you want to restore projects from.


### Database restoration scenario
Imagine you've found that an entire timeline has been deleted and has actually been missing for a while... in fact, you don't even know how long it's been missing for. Without a project backup you'll have to restore a database backup. Potentially the steps for that can look like this:

> 1. Restore the DB to a free host system
> 2. Try restoring a DB backup a few days older than the first backup.
> 3. Yay! You found the timeline, but unfortunately not all the changes are there. Try another backup.
> 4. Perfect! Found it. Alright, export a DaVinci Resolve timeline file.
> 5. Stop and remove the temporary database server.
> 6. Import the exported timeline into the current project on the production DB.

Second try might be pretty lucky if it's a long running project.
Therein lies one of the main benefits of running Rex. If you have project backups running alongside database backups, you can much more easily roll-back a single project.

## How does it work?
Run `rex up` and Rex runs as a background process using a given schedule to trigger actions.
When a scheduled backup event is reached, Rex sends you a desktop notification reminding you that a backup is ready. It waits for 30 seconds (or however long you set it to) and then exports the DaVinci Resolve project file, as well as an md5 checksum of the backup alongside it.


## Roadmap
- [x] CLI 
- [x] Rest API
- [x] Scheduled backups
- [x] YAML settings - app configuration with validation and default settings
- [ ] De-duplication - Check latest backup is not a duplicate of the last. Discard and symlink to save space.
- [ ] Scheduled checksum verification - automated periodic integrity checks
- [ ] Soft-schedule - wait a specified duration for decreased user-activity before exporting
- [ ] Automatic filtered uploads to cloud storage
- [ ] Nice little web GUI to make changes

## Installation

> **Warning**
>
> Currently only Resolve 18 is supported. Resolve 17 and older require Python 3.6, which is now EOL. Some dependencies have started dropping support for it. 
> A Resolve 17 branch doesn't currently exist, and will not unless someone asks nicely for it or forks the project.

Install the latest version of Python. You can use official installers or pyenv. Add it to path.
Rex CLI is bundled with Rex to control it. Install it with pipx.

```
pipx install git+https://github.com/in03/rex

# OR

pipx install git+https://github.com/in03/rex@resolve-17
```

## Why 'Rex'?
CLI entrypoints are like domain names. You want them short, memorable and it's nice if you can type them with one hand.
It's also kind of an awkward acronym derived from **R**esolve Project **EX**porter.
