# coding=utf8
""" Simple UI for Time logging """
import json
import logging
import os
import os.path
import threading
import time
import webbrowser
from datetime import date
from os.path import exists, expanduser

import PySimpleGUI as sg

home_dir = expanduser("~") + "/whatubinup2/"
reports_dir = home_dir + "reports/"
config_dir = home_dir + "config/"
logs_dir = home_dir + "logs/"

WEBSITE_LINK = "https://teamjtharrison.github.io/whatubinup2"
AUTHOR_LINK = "https://readme.tjth.co"

today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)
big_font = ("Open Sans", 25)

sg.LOOK_AND_FEEL_TABLE["WUBU2"] = {
    "BACKGROUND": "#96C5F7",
    "TEXT": "#F2F4FF",
    "INPUT": "#A9D3FF",
    "TEXT_INPUT": "#F2F4FF",
    "SCROLL": "#99CC99",
    "BUTTON": ("#A9D3FF", "#FFFFFF"),
    "PROGRESS": ("# D1826B", "# CC8019"),
    "BORDER": 0,
    "SLIDER_DEPTH": 1,
    "PROGRESS_DEPTH": 0,
}
sg.theme("wubu2")

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
    check_for_dir(config_dir)
    try:
        with open(config_dir + "bins.json", encoding="utf-8") as config:
            config = json.load(config)
    except FileNotFoundError:
        logging.info("bins.json config missing, generating from skeleton")
        with open(config_dir + "bins.json", "w", encoding="UTF-8") as config_file:
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
    check_for_dir(config_dir)
    try:
        with open(config_dir + "all.json", encoding="utf-8") as config:
            config = json.load(config)
    except FileNotFoundError:
        logging.info("all.json config missing, generating from skeleton")
        with open(config_dir + "all.json", "w", encoding="UTF-8") as config_file:
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
        [sg.Text("Settings", font=big_font)],
        [
            sg.Text(
                "Total Hours", font=font, tooltip=config["total_hours"]["description"]
            ),
            sg.InputText(default_text=config["total_hours"]["value"], font=font),
        ],
        [
            sg.Text(
                "Reminder Minutes",
                font=font,
                tooltip=config["reminder_minutes"]["description"],
            ),
            sg.InputText(default_text=config["reminder_minutes"]["value"], font=font),
        ],
        [sg.Text("Bins", font=big_font)],
        [
            [
                sg.Text("System Name: " + time_bin["name"], font=font),
                sg.Text("Description: " + time_bin["description"], font=font),
                sg.Button(
                    "Edit " + time_bin["nice_name"],
                    font=font,
                    tooltip="Edit bin settings for " + time_bin["nice_name"],
                ),
                sg.Button(
                    "Delete " + time_bin["nice_name"],
                    font=font,
                    tooltip="Delete bin " + time_bin["nice_name"],
                ),
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
    if event == sg.WIN_CLOSED:
        settings_window.close()
    else:
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
            with open(config_dir + "all.json", "w", encoding="UTF-8") as config_file:
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
                            sg.InputText(
                                default_text=edit_bin["description"], font=font
                            ),
                        ],
                        [sg.Button("Save", font=font)],
                    ]
            edit_bin_window = sg.Window(
                "Edit bin", edit_bin_layout, use_default_focus=False, finalize=True
            )
            event, bin_setting_values = edit_bin_window.read()
            if event == sg.WIN_CLOSED:
                settings_window.close()
            if event == "Save":
                new_bin_config = {
                    "name": bin_setting_values[1],
                    "nice_name": bin_setting_values[0],
                    "description": bin_setting_values[2],
                }
                with open(
                    config_dir + "/bins.json", "r+", encoding="UTF-8"
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
                        config_dir + "bins.json", "r+", encoding="UTF-8"
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
                    config_dir + "bins.json", "r+", encoding="UTF-8"
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
    check_for_dir(reports_dir)
    try:
        with open(reports_dir + today_date + ".json", encoding="utf-8") as report:
            report = json.load(report)
    except FileNotFoundError:
        logging.info("Generating report file on first run for today")
        with open(
            reports_dir + today_date + ".json", "w", encoding="UTF-8"
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
    files = os.listdir(reports_dir)
    paths = [os.path.join(reports_dir, basename) for basename in files]
    paths.sort(key=os.path.getctime)
    historic_report_list = []
    for path in paths:
        file_name = path.split("/")[-1].replace(".json", "")
        with open(path, "r", encoding="UTF-8") as historic_report_item:
            report_json = json.load(historic_report_item)
            report_text = ""
            for report_item in report_json:
                report_text += (
                    report_item + " : " + str(report_json[report_item]) + " \n"
                )
            layout = [[sg.T(report_text, font=font)]]
            historic_report_list.append([sg.Tab(file_name, layout, font=font)])
    historic_report_frame = [[sg.TabGroup(historic_report_list, font=font)]]
    report_layout = [
        [sg.Text("Todays", font=big_font)],
        [
            [
                sg.Text(
                    time_bin + ": " + str(json.loads(get_report())[time_bin]),
                    font=font,
                )
            ]
            for time_bin in json.loads(get_report())
        ],
        [sg.Frame("Historic Reports", historic_report_frame, font=font)],
    ]
    report_window = sg.Window(
        "Time Report", report_layout, use_default_focus=False, finalize=True
    )
    report_window.read()

    report_window.close()


def show_about():
    """Popup modal with the about page for the app"""
    about_layout = [
        [sg.Text("About WUBU2", font=big_font)],
        [
            sg.Text(
                (
                    "WUBU2 was written to fit the need of a small"
                    "app to log times into big buckets during a working day"
                ),
                font=font,
            )
        ],
        [
            sg.Text("App website: ", font=font),
            sg.Text(WEBSITE_LINK, font=font, enable_events=True, key="WEBSITE_LINK"),
        ],
        [
            sg.Text("About the Author: ", font=font),
            sg.Text(AUTHOR_LINK, font=font, enable_events=True, key="AUTHOR_LINK"),
        ],
    ]
    about_window = sg.Window(
        "About WUBU2", about_layout, use_default_focus=False, finalize=True
    )
    event, about_values = about_window.read()
    if event == "WEBSITE_LINK":
        logging.debug("About button clicked, details: %s", about_values)
        webbrowser.open(WEBSITE_LINK)
    if event == "AUTHOR_LINK":
        webbrowser.open(AUTHOR_LINK)

    about_window.close()


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
        while True:
            if self.stopped():
                logging.info("NotifyThread stopping")
                break
            config = json.loads(get_config())
            time_since = round((time.time() - start_time) / 60, 1)
            if time_since > float(config["reminder_minutes"]["value"]):
                logging.debug("Required time elapsed, triggering notification")
                break
            else:
                remaining_time = round(
                    float(config["reminder_minutes"]["value"]) - time_since, 1
                )
                logging.debug(
                    "Not yet ready to notify, %s minutes left", remaining_time
                )
                time.sleep(1)


def main():
    """Main app launch function"""
    logging.info("Getting config")
    get_config()
    logging.info("Getting bins")
    get_bins()
    main_layout = [
        [
            [
                sg.Button(
                    "Log " + time_bin["nice_name"],
                    font=font,
                    tooltip="Log time in " + time_bin["nice_name"] + " bin",
                )
            ]
            for time_bin in json.loads(get_bins())["time_bins"]
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
        [sg.Button("About", font=font, tooltip="About the app")],
        [sg.Button("Exit", font=font, tooltip="Exit the app")],
    ]
    logging.info("Launching client")
    main_window = sg.Window(
        "WUBU2", main_layout, keep_on_top=True, location=(1000, 200)
    )
    first_run = True
    while True:
        today_report = json.loads(get_report())
        current_config = json.loads(get_config())
        list_bins = json.loads(get_bins())["time_bins"]

        if len(threading.enumerate()) < 2:
            if not first_run:
                sg.Popup("Log your time!", font=font)
                logging.info("Time logging prompt acknowledged")
            notify_thread_manage = NotifyThread()
            notify_thread_manage.start()
            first_run = False
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
        if event == "About":
            show_about()
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
