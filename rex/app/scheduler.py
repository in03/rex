from time import sleep
import requests
from schedule import repeat, every, run_pending
from notifypy import Notify
from rex.settings.manager import SettingsManager
import chime

settings = SettingsManager()
frequency = settings["schedule"]["frequency_in_minutes"]
countdown_warning = settings["schedule"]["countdown_warning"]

chime.theme("mario")
notification = Notify()
notification.title = "Rex Scheduler"

tld = f"http://{settings['server']['ip']}:{settings['server']['port']}"


@repeat(every(frequency).minutes)
def scheduled_backup():

    # Remind user of scheduled backup
    if countdown_warning > 0:

        notification.message = f"Scheduled backup in {countdown_warning} seconds"
        notification.send()

        chime.info()
        sleep(countdown_warning)  # 30

    notification.message = f"Backing up! Take a brain-break."
    notification.send()

    # Backup
    success = requests.get(f"{tld}/backup", timeout=120).json()
    if success:

        chime.success()
        notification.message = "Successfully backed up"
        notification.send()

    else:

        chime.error()
        notification.message = (
            "Uh-oh! Something went wrong.\n"
            "Please check your project exists, is open, output path exists\n"
            "and try again manually with 'rex backup'"
        )
        notification.send()


while True:
    run_pending()
