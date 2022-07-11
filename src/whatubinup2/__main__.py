""" Simple UI for Time logging """
import json
import logging
import os
import os.path
import threading
import time
from datetime import date
from os.path import exists, expanduser

import file_ops
import PySimpleGUI as sg
import shows

home_dir = expanduser("~") + "/whatubinup2/"
reports_dir = home_dir + "reports/"
config_dir = home_dir + "config/"
tmp_dir = home_dir + "tmp/"
logs_dir = home_dir + "logs/"

today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)
big_font = ("Open Sans", 25)
sg.theme("DarkGrey4")

# Check for home dir
if not exists(home_dir):
    os.mkdir(home_dir)

# Check for logs dir
if not exists(logs_dir):
    os.mkdir(logs_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(logs_dir + "application_" + today_date + ".log"),
        logging.StreamHandler(),
    ],
)


def check_for_dir(full_dir):
    """Function to create missing directories"""
    if not exists(full_dir):
        logging.info("%s dir does not exist, recreating..", full_dir)
        os.mkdir(full_dir)
        logging.info("%s dir created", full_dir)


class NotifyThread(threading.Thread):
    """Class used for management of notification thread"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stopper = threading.Event()

    def stop(self):
        """Stop function"""
        logging.info("NotifyThread will exit on next cycle")
        self._stopper.set()

    def stopped(self):
        """Check if stopped"""
        return self._stopper.isSet()

    def run(self):
        start_time = time.time()
        check_for_dir(tmp_dir)
        while True:
            if self.stopped():
                logging.info("NotifyThread stopping")
                return
            config = json.loads(file_ops.get_config())
            time_since = round((time.time() - start_time) / 60, 1)
            if time_since > float(config["reminder_minutes"]["value"]):
                with open(
                    tmp_dir + "do_notify", "w", encoding="UTF-8"
                ) as do_notify_file:
                    do_notify_file.write(str(time.time()))
                    start_time = time.time()
                    logging.debug("Notification sent, timer restarting")
                    continue
            else:
                remaining_time = round(
                    float(config["reminder_minutes"]["value"]) - time_since, 1
                )
                logging.debug("Not ready to notify, %s minutes left", remaining_time)
                time.sleep(9)


def main():
    """Main app launch function"""
    start_notifier = True
    logging.info("Getting config")
    file_ops.get_config()
    logging.info("Getting bins")
    file_ops.get_bins()
    main_layout = [
        [
            [
                sg.Button(
                    "Log " + time_bin["nice_name"],
                    font=font,
                    tooltip="Log time in " + time_bin["nice_name"] + " bin",
                )
            ]
            for time_bin in json.loads(file_ops.get_bins())["time_bins"]
        ],
        [sg.Text("", font=font, key="current_total")],
        [
            sg.Button(
                "Report", font=font, tooltip="Show a report of current time binned"
            )
        ],
        [
            sg.Button(
                "Settings", font=font, tooltip="Edit app settings and configure bins"
            )
        ],
        [sg.Button("Exit", font=font, tooltip="Exit the app")],
    ]
    logging.info("Launching client")
    main_window = sg.Window(
        "What U bin up 2", main_layout, keep_on_top=True, location=(1000, 200)
    )
    while True:
        today_report = json.loads(file_ops.get_report())
        current_config = json.loads(file_ops.get_config())
        list_bins = json.loads(file_ops.get_bins())["time_bins"]
        if start_notifier is True:
            start_notifier = False
            ## Launch thread
            notify_thread_manage = NotifyThread()
            notify_thread_manage.start()

        if exists(tmp_dir + "do_notify"):
            sg.Popup("Log your time!", font=font)
            os.remove(tmp_dir + "do_notify")
        working_hours = current_config["total_hours"]["value"]
        event, main_values = main_window.read(timeout=2)
        if main_values != {}:
            logging.debug("Event triggered, entered values: %s", main_values)
        try:
            hours_spent = 0
            for today_bin in today_report:
                hours_spent += today_report[today_bin]
        except KeyError:
            hours_spent = 0
        main_window["current_total"].update(
            "Total logged: " + str(hours_spent) + "/" + str(working_hours)
        )
        time_logged = False
        if event in (sg.WIN_CLOSED, "Exit"):
            logging.info("Exit requested, closing NotifyThread")
            sg.PopupNoButtons(
                "Exiting, please wait for notify thread to close..",
                font=font,
                auto_close_duration=2,
                auto_close=True,
            )
            notify_thread_manage.stop()
            notify_thread_manage.join()
            logging.info("Exiting")
            break
        if event == "Report":
            shows.show_report()
        if event == "Settings":
            shows.show_settings()
        if event.startswith("Log"):
            # Iterate over bins looking for event
            for event_bin in list_bins:
                raw_event = event.replace("Log ", "")
                if raw_event == event_bin["nice_name"]:
                    try:
                        today_report[event_bin["name"]] = (
                            today_report[event_bin["name"]] + 1
                        )
                    except KeyError:
                        today_report[event_bin["name"]] = 1
                    new_total = today_report[event_bin["name"]]
                    logging.info("Meeting time logged")
                    time_logged = True
        if time_logged is True:
            with open(
                reports_dir + today_date + ".json",
                "w",
                encoding="UTF-8",
            ) as report_file:
                report_file.write(json.dumps(today_report))
                report_file.close()
            sg.PopupNoButtons(
                "New total for " + event + " is " + str(new_total),
                font=font,
                auto_close_duration=1,
                auto_close=True,
            )
    main_window.close()


if __name__ == "__main__":
    logging.info("Whatubinup2 starting..")
    main()
