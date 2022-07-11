""" Simple UI for Time logging """
import json
import logging
import os
import threading
import time
from datetime import date
from os.path import exists, expanduser

import PySimpleGUI as sg

home_dir = expanduser("~") + "/whatubinup2/"

today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)
big_font = ("Open Sans", 25)
sg.theme("DarkTeal9")


# Check for logs dir
if not exists(home_dir + "logs"):
    os.mkdir(home_dir + "logs")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(home_dir + "logs/application_" + today_date + ".log"),
        logging.StreamHandler(),
    ],
)


def check_for_dir(subdir):
    """Function to create missing directories"""
    if not exists(home_dir + subdir):
        logging.info("%s dir does not exist, recreating..", subdir)
        os.mkdir(home_dir + subdir)
        logging.info("%s dir created", subdir)


default_config = json.dumps(
    {
        "total_hours": {
            "description": "Total number of hours in working day",
            "value": 8,
        },
        "reminder_minutes": {
            "description": "After how many minutes would you like a reminder",
            "value": 10,
        },
    }
)


def get_bins():
    """Function to get bins from local config"""
    check_for_dir("config")
    try:
        with open(home_dir + "config/bins.json", encoding="utf-8") as config:
            config = json.load(config)
    except FileNotFoundError:
        logging.info("bins.json config missing, generating from skeleton")
        with open(home_dir + "config/bins.json", "w", encoding="UTF-8") as config_file:
            config_file.write(
                json.dumps(
                    {
                        "time_bins": [
                            {
                                "name": "default",
                                "nice_name": "Default",
                                "description": "Default time bin",
                            }
                        ]
                    }
                )
            )
            config_file.close()
        logging.info("Default bins created!")
        config = default_config
    return json.dumps(config)


def get_config():
    """Function to get configuration from local config"""
    check_for_dir("config")
    try:
        with open(home_dir + "config/all.json", encoding="utf-8") as config:
            config = json.load(config)
    except FileNotFoundError:
        logging.info("all.json config missing, generating from skeleton")
        with open(home_dir + "config/all.json", "w", encoding="UTF-8") as config_file:
            config_file.write(default_config)
            config_file.close()
        logging.info("Default config applied!")
        config = default_config
    return json.dumps(config)


def show_settings():
    """Popup modal with current settings"""
    logging.info("Settings opened")
    config = json.loads(get_config())
    settings_layout = [
        [sg.Text("Settings", font=font)],
        [
            sg.Text("Total Hours", font=font),
            sg.Text(
                "?",
                background_color="magenta",
                tooltip=config["total_hours"]["description"],
            ),
            sg.InputText(default_text=config["total_hours"]["value"], font=font),
        ],
        [
            sg.Text("Reminder Minutes", font=font),
            sg.Text(
                "?",
                tooltip=config["reminder_minutes"]["description"],
                background_color="magenta",
            ),
            sg.InputText(default_text=config["reminder_minutes"]["value"], font=font),
        ],
        [sg.Text("Bins", font=big_font)],
        [
            [
                sg.Text("System Name: " + time_bin["name"], font=font),
                sg.Text("Description: " + time_bin["description"], font=font),
                sg.Button("Edit " + time_bin["nice_name"], font=font),
                sg.Button("Delete " + time_bin["nice_name"], font=font),
            ]
            for time_bin in json.loads(get_bins())["time_bins"]
        ],
        [
            sg.Button("Add bin", font=font),
        ],
        [sg.Button("Save", font=font)],
    ]
    settings_window = sg.Window(
        "WUBU2 Settings", settings_layout, use_default_focus=False, finalize=True
    )
    event, setting_values = settings_window.read()

    if event == "Save":
        new_config = json.dumps(
            {
                "total_hours": {
                    "description": "Total number of hours in working day",
                    "value": setting_values[0],
                },
                "reminder_minutes": {
                    "description": "After how many minutes would you like a reminder",
                    "value": setting_values[1],
                },
            }
        )
        with open(home_dir + "config/all.json", "w", encoding="UTF-8") as config_file:
            config_file.write(new_config)
            config_file.close()
        logging.info("New settings applied: %s", new_config)
    if event.startswith("Edit"):
        for edit_bin in json.loads(get_bins())["time_bins"]:
            raw_event = event.replace("Edit ", "")
            if raw_event == edit_bin["nice_name"]:
                edit_bin_layout = [
                    [
                        sg.Text(
                            "Update fields below to edit " + edit_bin["nice_name"],
                            font=font,
                        ),
                    ],
                    [
                        sg.Text("Nice name:", font=font),
                        sg.InputText(default_text=edit_bin["nice_name"], font=font),
                    ],
                    [
                        sg.Text("System name:", font=font),
                        sg.InputText(default_text=edit_bin["name"], font=font),
                    ],
                    [
                        sg.Text("Description:", font=font),
                        sg.InputText(default_text=edit_bin["description"], font=font),
                    ],
                    [sg.Button("Save", font=font)],
                ]
        edit_bin_window = sg.Window(
            "Edit bin", edit_bin_layout, use_default_focus=False, finalize=True
        )
        event, bin_setting_values = edit_bin_window.read()
        if event == "Save":
            new_bin_config = {
                "name": bin_setting_values[1],
                "nice_name": bin_setting_values[0],
                "description": bin_setting_values[2],
            }
            with open(
                home_dir + "config/bins.json", "r+", encoding="UTF-8"
            ) as bin_config:
                bin_config_data = json.load(bin_config)
                list_position = 0
                for bin_config_item in bin_config_data["time_bins"]:
                    if edit_bin["name"] != bin_config_item["name"]:
                        list_position += 1
                bin_config_data["time_bins"][list_position] = new_bin_config

                bin_config.seek(0)
                bin_config.write(json.dumps(bin_config_data))
                bin_config.truncate()
                sg.Popup("Bin edited successfully!", font=font)
            logging.info("New bin settings for applied: %s", new_bin_config)
        edit_bin_window.close()

    if event.startswith("Delete"):
        del_pos = 0
        for del_bin in json.loads(get_bins())["time_bins"]:
            raw_event = event.replace("Delete ", "")
            if raw_event == del_bin["nice_name"]:
                with open(
                    home_dir + "config/bins.json", "r+", encoding="UTF-8"
                ) as bin_config:
                    bin_config_data = json.load(bin_config)
                    bin_config_data["time_bins"].pop(del_pos)

                    bin_config.seek(0)
                    bin_config.write(json.dumps(bin_config_data))
                    bin_config.truncate()
                    sg.Popup("Bin has been deleted!", font=font)
                    logging.info("Bin has been deleted: %s", bin_config_data)
            else:
                del_pos += 1

    if event == ("Add bin"):
        add_bin_layout = [
            [
                sg.Text("Update fields below to create a new bin", font=font),
            ],
            [
                sg.Text("Nice name:", font=font),
                sg.InputText(font=font),
            ],
            [
                sg.Text("System name:", font=font),
                sg.InputText(font=font),
            ],
            [
                sg.Text("Description:", font=font),
                sg.InputText(font=font),
            ],
            [sg.Button("Save", font=font)],
        ]
        add_bin_window = sg.Window(
            "Add bin", add_bin_layout, use_default_focus=False, finalize=True
        )
        event, add_bin_values = add_bin_window.read()
        if event == "Save":
            add_bin_config = {
                "name": add_bin_values[1],
                "nice_name": add_bin_values[0],
                "description": add_bin_values[2],
            }
            with open(
                home_dir + "config/bins.json", "r+", encoding="UTF-8"
            ) as bin_config:
                bin_config_data = json.load(bin_config)

                bin_config_data["time_bins"].append(add_bin_config)

                bin_config.seek(0)
                bin_config.write(json.dumps(bin_config_data))
                bin_config.truncate()
                sg.Popup(
                    "New bin added (NOTE: This requires an app reload)!", font=font
                )
        logging.info("New bin created: %s", add_bin_config)
        add_bin_window.close()
    settings_window.close()


def get_report():
    """Function to get or generate todays report"""
    check_for_dir("reports")
    try:
        with open(
            home_dir + "reports/" + today_date + ".json", encoding="utf-8"
        ) as report:
            report = json.load(report)
    except FileNotFoundError:
        logging.info("Generating report file on first run for today")
        with open(
            home_dir + "reports/" + today_date + ".json", "w", encoding="UTF-8"
        ) as report_file:

            report_skeleton = {}

            for update_bin in json.loads(get_bins())["time_bins"]:
                report_skeleton.update({update_bin["name"]: 0})

            report_file.write(json.dumps(report_skeleton))
            report_file.close()
        logging.info("Default report_skeleton applied to report!")
        report = report_skeleton
    return json.dumps(report)


def show_report():
    """Popup modal with current time logging stats"""
    logging.info("Report opened")
    today_report = json.loads(get_report())
    layout = [
        [
            [
                sg.Text(
                    time_bin["nice_name"] + ": " + str(today_report[time_bin["name"]]),
                    font=font,
                )
            ]
            for time_bin in json.loads(get_bins())["time_bins"]
        ]
    ]
    report_window = sg.Window(
        "Time Report", layout, use_default_focus=False, finalize=True
    )
    report_window.read()
    report_window.close()


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
        check_for_dir("tmp")
        while True:
            if self.stopped():
                logging.info("NotifyThread stopping")
                return
            config = json.loads(get_config())
            time_since = round((time.time() - start_time) / 60, 1)
            if time_since > float(config["reminder_minutes"]["value"]):
                with open(
                    home_dir + "tmp/do_notify", "w", encoding="UTF-8"
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
    get_config()
    logging.info("Getting bins")
    get_bins()
    main_layout = [
        [
            [sg.Button("Log " + time_bin["nice_name"], font=font)]
            for time_bin in json.loads(get_bins())["time_bins"]
        ],
        [sg.Text("", font=font, key="current_total")],
        [sg.Button("Report", font=font)],
        [sg.Button("Settings", font=font)],
        [sg.Button("Exit", font=font)],
    ]
    logging.info("Launching client")
    main_window = sg.Window("What U bin up 2", main_layout, keep_on_top=True)
    while True:
        today_report = json.loads(get_report())
        current_config = json.loads(get_config())
        list_bins = json.loads(get_bins())["time_bins"]
        if start_notifier is True:
            start_notifier = False
            ## Launch thread
            notify_thread_manage = NotifyThread()
            notify_thread_manage.start()

        if exists(home_dir + "tmp/do_notify"):
            sg.Popup("Log your time!", font=font)
            os.remove(home_dir + "tmp/do_notify")
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
            show_report()
        if event == "Settings":
            show_settings()
        if event.startswith("Log"):
            # Iterate over bins looking for event
            for bin in list_bins:
                raw_event = event.replace("Log ", "")
                if raw_event == bin["nice_name"]:
                    try:
                        today_report[bin["name"]] = today_report[bin["name"]] + 1
                    except KeyError:
                        today_report[bin["name"]] = 1
                    new_total = today_report[bin["name"]]
                    logging.info("Meeting time logged")
                    time_logged = True
        if time_logged is True:
            with open(
                home_dir + "reports/" + today_date + ".json",
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
