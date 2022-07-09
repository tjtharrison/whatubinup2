""" Simple UI for Time logging """
import json
import logging
import os
import time
from datetime import date
from os.path import exists, expanduser
from threading import Thread

import PySimpleGUI as sg

home_dir = expanduser("~") + "/whatubinup2/"

today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)

sg.theme("DarkTeal9")

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
        "time_bins": {
            "meetings": {
                "description": "Time spent in meetings",
                "nice_name": "Meetings",
            },
            "planned_dev": {
                "description": "Planned developer time",
                "nice_name": "Planned Dev Time",
            },
            "unplanned_dev": {
                "description": "Unplanned developer time (Eg support)",
                "nice_name": "Unplanned Dev Time",
            },
        },
    }
)

# Setup dirs
if not exists(home_dir):
    dirs = [
        home_dir,
        home_dir + "tmp",
        home_dir + "config",
        home_dir + "reports",
        home_dir + "logs",
    ]
    for my_dir in dirs:
        os.mkdir(my_dir)
    with open(
        home_dir + "config/all.json", "w", encoding="UTF-8"
    ) as default_config_file:
        default_config_file.write(default_config)
        default_config_file.close()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(home_dir + "logs/application_" + today_date + ".log"),
        logging.StreamHandler(),
    ],
)

main_layout = [
    [sg.Button("Meetings", font=font)],
    [sg.Button("Planned Dev", font=font)],
    [sg.Button("Unplanned Dev", font=font)],
    [sg.Text("", font=font, key="current_total")],
    [sg.Button("Report", font=font)],
    [sg.Button("Settings", font=font)],
    [sg.Button("Exit", font=font)],
]


def get_config():
    """Function to get configuration from local config"""
    try:
        with open(home_dir + "config/all.json", encoding="utf-8") as config:
            config = json.load(config)
    except FileNotFoundError:
        logging.info("Generating config file on first run")
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
        [sg.Button("Submit", font=font)],
    ]
    settings_window = sg.Window(
        "Time Report", settings_layout, use_default_focus=False, finalize=True
    )
    event, setting_values = settings_window.read()

    if event == "Submit":
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
    settings_window.close()


def get_report():
    """Function to get or generate todays report"""
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
            report_skeleton = json.dumps(
                {"meetings": 0, "planned_dev": 0, "unplanned_dev": 0}
            )
            report_file.write(report_skeleton)
            report_file.close()
        logging.info("Default report_skeleton applied to report!")
        report = report_skeleton
    return json.dumps(report)


def do_notify(start_time):
    """Function to setup notifications in thread"""
    while True:
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


def show_report():
    """Popup modal with current time logging stats"""
    logging.info("Report opened")
    today_report = json.loads(get_report())
    layout = [
        [sg.Text("Meetings: " + str(today_report["meetings"]), font=font)],
        [sg.Text("Planned Dev: " + str(today_report["planned_dev"]), font=font)],
        [sg.Text("Support: " + str(today_report["unplanned_dev"]), font=font)],
    ]
    report_window = sg.Window(
        "Time Report", layout, use_default_focus=False, finalize=True
    )
    report_window.read()
    report_window.close()


def main():
    """Main app launch function"""
    main_window = sg.Window(
        "What U bin up 2", main_layout, keep_on_top=True, size=(180, 250)
    )
    start_notifier = True
    while True:
        today_report = json.loads(get_report())
        current_config = json.loads(get_config())
        if start_notifier is True:
            start_notifier = False
            notify_thread = Thread(
                target=do_notify,
                args=(time.time(),),
            )
            notify_thread.start()

        if exists(home_dir + "tmp/do_notify"):
            sg.Popup("Log your time!", font=font)
            os.remove(home_dir + "tmp/do_notify")
        working_hours = current_config["total_hours"]["value"]
        event, values = main_window.read(timeout=2)
        # Avoiding race condition on first launch
        try:
            hours_spent = (
                today_report["meetings"]
                + today_report["planned_dev"]
                + today_report["unplanned_dev"]
            )
        except TypeError:
            logging.info("No hours reported yet")
            hours_spent = 0
        main_window["current_total"].update(
            "Total logged: " + str(hours_spent) + "/" + str(working_hours)
        )

        time_logged = False
        if event in (sg.WIN_CLOSED, "Exit"):
            logging.debug("New event: %s", values)
            print("Mischief managed")
            notify_thread.join()
            break
        if event == "Report":
            show_report()
        if event == "Settings":
            show_settings()
        if event == "Meetings":
            today_report["meetings"] = today_report["meetings"] + 1
            new_total = today_report["meetings"]
            logging.info("Meeting time logged")
            time_logged = True
        if event == "Planned Dev":
            today_report["planned_dev"] = today_report["planned_dev"] + 1
            new_total = today_report["planned_dev"]
            logging.info("Planned Dev time logged")
            time_logged = True
        if event == "Unplanned Dev":
            today_report["unplanned_dev"] = today_report["unplanned_dev"] + 1
            new_total = today_report["unplanned_dev"]
            logging.info("Unplanned Dev time logged")
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
    main()
