import logging
import sys
import time

from notifypy import Notify
from rich.logging import RichHandler
from rich.prompt import Prompt
import hashlib


def md5_checksum(file_):
    hash_md5 = hashlib.md5()
    with open(file_, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


import hashlib

h = hashlib.new("sha256")  # sha256 can be replaced with diffrent algorithms
h.update("Hello World".encode())  # give a encoded string. Makes the String to the Hash
print(h.hexdigest())  # Prints the Hash


def setup_rich_logging():

    """Set logger to rich, allowing for console markup."""

    FORMAT = "%(message)s"
    logging.basicConfig(
        level="WARNING",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_extra_lines=1,
                markup=True,
            )
        ],
    )


setup_rich_logging()
logger = logging.getLogger(__name__)


def app_exit(level: int = 0, timeout: int = -1, cleanup_funcs: list = []):

    """
    Exit function to allow time to
    read console output if necessary before exit.
    Specify negative timeout to prompt exit instead of timeout.
    Provide a list of functions to call on cleanup if necessary.
    """

    # Run any cleanup functions
    if cleanup_funcs:

        for x in cleanup_funcs:
            if x is not None:
                x()

    if timeout < 0:
        answer = Prompt.ask("Press [yellow]ENTER[/] to exit")
        sys.exit(level)

    else:

        for i in range(timeout, -1, -1):

            time.sleep(1)
            sys.stdout.write(f"\rExiting in " + str(i))

        # Erase last line
        sys.stdout.write("\x1b[1A")
        sys.stdout.write("\x1b[2K")

    sys.exit(level)


def notify(message: str, title: str = "Resolve Proxy Encoder"):
    """Cross platform system notification

    Args:
        message(str): Message to display
        title(str): Title of notification

    Returns:
        True/False(bool): Success/Failure

    Raises:
        none

    """

    try:

        notification = Notify()
        notification.title = title
        notification.message = message
        notification.send(block=False)

    except Exception as e:
        logger.exception(f"[red] :warning: Couldn't send notification.[/]\n{e}")
        return False

    return True
