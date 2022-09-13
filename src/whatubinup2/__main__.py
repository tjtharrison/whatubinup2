# coding=utf8
""" Simple UI for Time logging """
import json
import logging
import os
import os.path
import threading
import time
import webbrowser
from datetime import date, datetime
from os.path import exists, expanduser

import PySimpleGUI as sg
import requests

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
    level=logging.INFO,
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
        "email_address": "",
        "license_level": "free",
        "license_code": "",
        "license_validated": "",
        "api_server": "https://api-wubu2.tjth.co",
        "historic_reports_to_show": 7,
        "time_bins": [
            {
                "name": "default",
                "nice_name": "Default",
                "description": "Default time bin",
            }
        ],
    }
)


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
    config = json.loads(get_config())
    while True:
        settings_layout = [
            [sg.Text("Settings", font=big_font)],
            [
                sg.Text(
                    "Total Hours",
                    font=font,
                    tooltip=config["total_hours"]["description"],
                ),
                sg.InputText(default_text=config["total_hours"]["value"], font=font),
            ],
            [
                sg.Text(
                    "Reminder Minutes",
                    font=font,
                    tooltip=config["reminder_minutes"]["description"],
                ),
                sg.InputText(
                    default_text=config["reminder_minutes"]["value"], font=font
                ),
            ],
            [
                sg.Text(
                    "Historic report maximum",
                    font=font,
                    tooltip="How many historic reports to display in Reports",
                ),
                sg.InputText(
                    default_text=config["historic_reports_to_show"], font=font
                ),
            ],
            [sg.Text("Licensing", font=big_font)],
            [
                sg.Text("License level: ", font=font),
                sg.Text(config["license_level"], font=font),
            ],
            [
                sg.Text(
                    "Email Address",
                    font=font,
                    tooltip="Registed email address for wubu2",
                ),
                sg.InputText(default_text=config["email_address"], font=font),
            ],
            [
                sg.Text(
                    "License Code",
                    font=font,
                    tooltip="License code for wubu2",
                ),
                sg.InputText(default_text=config["license_code"], font=font),
            ],
            [
                sg.Button(
                    "Request License",
                    font=font,
                    tooltip="Will update with free license if no license present",
                )
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
                for time_bin in config["time_bins"]
            ],
            [
                sg.Button("Add bin", font=font),
            ],
            [sg.Button("Save", font=font)],
        ]
        settings_window = sg.Window(
            "WUBU2 Settings", settings_layout, use_default_focus=False, finalize=True
        )
        logging.info("Settings opened")
        event, setting_values = settings_window.read()
        if event == sg.WIN_CLOSED:
            settings_window.close()
            break
        else:
            if event == "Request License":
                url = config["api_server"] + "/api/auth/create"

                post_url = requests.post(url, json={"id": config["email_address"]})

                try:
                    response = json.loads(post_url.text)
                    status = response["status"]
                    details = response["details"]
                except json.JSONDecodeError:
                    status = "fail"
                    details = "Invalid response from api"

                if status == "ok":
                    with open(
                        config_dir + "/all.json", "r+", encoding="UTF-8"
                    ) as config_file:
                        config_file_data = json.load(config_file)
                        config_file_data["license_code"] = details["license_code"]
                        config_file.seek(0)
                        config_file.write(json.dumps(config_file_data))
                        config_file.truncate()
                        logging.info("Updated config with new license key")
                        post_url = requests.post(
                            config_file_data["api_server"] + "/api/config/upload",
                            json={
                                "id": config_file_data["email_address"],
                                "license": config_file_data["license_code"],
                                "config": config_file_data,
                            },
                        )
                else:
                    sg.Popup(
                        "License request unsuccessful: " + details,
                        font=font,
                    )

            if event == "Save":
                with open(
                    config_dir + "/all.json", "r+", encoding="UTF-8"
                ) as config_file:
                    config_file_data = json.load(config_file)
                    config_file_data["total_hours"]["value"] = setting_values[0]
                    config_file_data["reminder_minutes"]["value"] = setting_values[1]
                    config_file_data["historic_reports_to_show"] = int(
                        setting_values[2]
                    )
                    config_file_data["email_address"] = setting_values[3]
                    config_file_data["license_code"] = setting_values[4]
                    config_file.seek(0)
                    config_file.write(json.dumps(config_file_data))
                    config_file.truncate()
                    # Upload to cloud if paid
                    if config_file_data["license_level"] == "paid":
                        print("Got here")
                        post_url = requests.post(
                            config_file_data["api_server"] + "/api/config/upload",
                            json={
                                "id": config_file_data["email_address"],
                                "license": config_file_data["license_code"],
                                "config": config_file_data,
                            },
                        )
                        logging.info("Settings uploaded to Cloud")
                logging.info("New settings applied: %s", config_file_data)
            if event.startswith("Edit"):
                for edit_bin in config["time_bins"]:
                    raw_event = event.replace("Edit ", "")
                    if raw_event == edit_bin["nice_name"]:
                        edit_bin_layout = [
                            [
                                sg.Text(
                                    "Update fields below to edit "
                                    + edit_bin["nice_name"],
                                    font=font,
                                ),
                            ],
                            [
                                sg.Text("Nice name:", font=font),
                                sg.InputText(
                                    default_text=edit_bin["nice_name"], font=font
                                ),
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
                    break
                if event == "Save":
                    new_bin_config = {
                        "name": bin_setting_values[1],
                        "nice_name": bin_setting_values[0],
                        "description": bin_setting_values[2],
                    }
                    with open(
                        config_dir + "/all.json", "r+", encoding="UTF-8"
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
                        sg.Popup(
                            "Bin edited successfully! App reload required to display new name",
                            font=font,
                        )
                        post_url = requests.post(
                            bin_config_data["api_server"] + "/api/config/upload",
                            json={
                                "id": bin_config_data["email_address"],
                                "license": bin_config_data["license_code"],
                                "config": bin_config_data,
                            },
                        )
                    logging.info("New bin settings for applied: %s", new_bin_config)
                edit_bin_window.close()

            if event.startswith("Delete"):
                del_pos = 0
                for del_bin in config["time_bins"]:
                    raw_event = event.replace("Delete ", "")
                    if raw_event == del_bin["nice_name"]:
                        with open(
                            config_dir + "all.json", "r+", encoding="UTF-8"
                        ) as bin_config:
                            bin_config_data = json.load(bin_config)
                            bin_config_data["time_bins"].pop(del_pos)
                            bin_config.seek(0)
                            bin_config.write(json.dumps(bin_config_data))
                            bin_config.truncate()
                            sg.Popup("Bin has been deleted!", font=font)
                            logging.info("Bin has been deleted: %s", bin_config_data)
                            post_url = requests.post(
                                bin_config_data["api_server"] + "/api/config/upload",
                                json={
                                    "id": bin_config_data["email_address"],
                                    "license": bin_config_data["license_code"],
                                    "config": bin_config_data,
                                },
                            )
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
                        config_dir + "all.json", "r+", encoding="UTF-8"
                    ) as bin_config:
                        bin_config_data = json.load(bin_config)
                        # Validate bin nice name or system name
                        # does not exist already with the same name
                        okay_to_apply = True
                        for current_bin in bin_config_data["time_bins"]:
                            if (
                                current_bin["name"].lower() == add_bin_values[1].lower()
                                or current_bin["nice_name"].lower()
                                == add_bin_values[0].lower()
                            ):
                                popup_text = (
                                    "Bin cannot be created with the same name "
                                    "as a current bin (System name must be unique)"
                                )
                                okay_to_apply = False
                        if (
                            len(add_bin_values[0]) == 0
                            or len(add_bin_values[1]) == 0
                            or len(add_bin_values[2]) == 0
                        ):
                            popup_text = "All fields must be entered"
                            okay_to_apply = False

                        if okay_to_apply:
                            bin_config_data["time_bins"].append(add_bin_config)
                            bin_config.seek(0)
                            bin_config.write(json.dumps(bin_config_data))
                            bin_config.truncate()
                            popup_text = (
                                "New bin added "
                                "(NOTE: This requires an app reload to log time against)!"
                            )
                        post_url = requests.post(
                            bin_config_data["api_server"] + "/api/config/upload",
                            json={
                                "id": bin_config_data["email_address"],
                                "license": bin_config_data["license_code"],
                                "config": bin_config_data,
                            },
                        )
                        sg.Popup(popup_text, font=font)
                logging.info("New bin created: %s", add_bin_config)
                add_bin_window.close()

        settings_window.close()
        break


def show_ask_email():
    """Popup modal asking for email address"""
    logging.info("First launch, requesting email")
    enter_email_layout = [
        [
            sg.Text(
                "Enter email address for use of non-free features, leave blank otherwise..",
                font=font,
            )
        ],
        [
            sg.Text(
                "Email Address",
                font=font,
                tooltip="Email address used for non-free features",
            ),
            sg.InputText(font=font),
        ],
        [sg.Button("Save", font=font)],
    ]
    email_enter_window = sg.Window(
        "Enter email", enter_email_layout, use_default_focus=False, finalize=True
    )
    event, email_address_value = email_enter_window.read()
    if event == sg.WIN_CLOSED:
        email_enter_window.close()
    else:
        if event == "Save":
            if len(email_address_value[0]) == 0:
                entered_email_address = "unlicensed"
            else:
                entered_email_address = email_address_value[0]
            with open(config_dir + "/all.json", "r+", encoding="UTF-8") as all_config:
                all_config_data = json.load(all_config)
                all_config_data["email_address"] = entered_email_address
                all_config.seek(0)
                all_config.write(json.dumps(all_config_data))
                all_config.truncate()
                if entered_email_address == "unlicensed":
                    email_request_message = (
                        "No problem, only required for paid features!"
                    )
                else:
                    email_request_message = (
                        "Email address updated successfully!"
                        " (With whatever you entered.. We're not checking!"
                    )
                sg.Popup(email_request_message, font=font)

    email_enter_window.close()


def get_report():
    """Function to get or generate todays report"""
    check_for_dir(reports_dir)
    current_config = json.loads(get_config())
    try:
        with open(reports_dir + today_date + ".json", encoding="utf-8") as report:
            report = json.load(report)
    except FileNotFoundError:
        logging.info("Generating report file on first run for today")
        with open(
            reports_dir + today_date + ".json", "w", encoding="UTF-8"
        ) as report_file:
            report_skeleton = {}
            for update_bin in current_config["time_bins"]:
                report_skeleton.update({update_bin["name"]: 0})
            report_file.write(json.dumps(report_skeleton))
            report_file.close()
        logging.info("Default report_skeleton applied to report!")
        report = report_skeleton
    return json.dumps(report)


def show_report():
    """Popup modal with current time logging stats"""
    logging.info("Report opened")
    current_config = json.loads(get_config())
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
            historic_report_list.insert(0, [sg.Tab(file_name, layout, font=font)])
            historic_reports_to_show = current_config["historic_reports_to_show"]
            historic_report_list = historic_report_list[0:historic_reports_to_show]
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
    current_config = json.loads(get_config())

    about_layout = [
        [sg.Text("About WUBU2", font=big_font)],
        [
            sg.Text(
                (
                    "WUBU2 was written to fit the need of a small "
                    "app to log times into big buckets during a working day"
                ),
                font=font,
            )
        ],
        [
            sg.Text("License type: " + current_config["license_level"], font=font),
        ],
        [
            sg.Text(
                "License registered to: " + current_config["email_address"], font=font
            ),
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
                logging.info("Required time elapsed, triggering notification")
                break
            else:
                remaining_time = round(
                    float(config["reminder_minutes"]["value"]) - time_since, 1
                )
                logging.info("Not yet ready to notify, %s minutes left", remaining_time)
                time.sleep(1)


def check_licensing():
    """Function to check licensing against API"""
    date_format = "%Y-%m-%d %H:%M:%S"
    current_config = json.loads(get_config())
    now_time = datetime.now().strftime(date_format)
    now_time = datetime.strptime(now_time, date_format)

    try:
        # If not unlicensed
        if current_config["email_address"] != "unlicensed":
            if len(current_config["license_validated"]) == 0:
                validated_time = datetime.strptime(str(now_time), date_format)
            else:
                validated_time = datetime.strptime(
                    current_config["license_validated"], date_format
                )
            time_diff = now_time - validated_time
            # If never validated or validated > 1 minute ago
            if (
                len(current_config["license_validated"]) == 0
                or time_diff.total_seconds() / 60 > 0.1
            ):
                logging.info("Validating license..")

                url = current_config["api_server"] + "/api/auth/validate"

                post_url = requests.post(
                    url,
                    json={
                        "id": current_config["email_address"],
                        "license": current_config["license_code"],
                    },
                )

                try:
                    response = json.loads(post_url.text)
                    status = response["status"]
                    details = response["details"]
                except json.JSONDecodeError:
                    status = "fail"
                    details = "Invalid response from api"
                # License failed to validate
                with open(
                    config_dir + "/all.json", "r+", encoding="UTF-8"
                ) as all_config_license_val:
                    all_config_license_val_data = json.load(all_config_license_val)
                    all_config_license_val_data["license_validated"] = str(now_time)
                    if status == "ok":
                        all_config_license_val_data["license_level"] = response[
                            "details"
                        ]["license_status"]
                    all_config_license_val.seek(0)
                    all_config_license_val.write(
                        json.dumps(all_config_license_val_data)
                    )
                    all_config_license_val.truncate()
                logging.info("License validation complete - %s", str(details))
            else:
                status = "ok"
                details = "Not ready to validate license yet, time left: " + str(
                    time_diff.total_seconds() / 60
                )
        else:
            status = "ok"
            details = "Unlicensed email address"
    except Exception as error_message:
        status = "fail"
        details = "Something has gone wrong: " + str(error_message)

    response = json.dumps({"status": status, "details": details})
    return response


def main():
    """Main app launch function"""
    logging.info("Getting config")
    config = json.loads(get_config())
    main_layout = [
        [
            [
                sg.Button(
                    "Log " + time_bin["nice_name"],
                    font=font,
                    tooltip="Log time in " + time_bin["nice_name"] + " bin",
                )
            ]
            for time_bin in config["time_bins"]
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
        list_bins = config["time_bins"]

        # Check email address configured
        if first_run:
            if len(current_config["email_address"]) < 1:
                show_ask_email()

        # Sync settings
        if first_run:
            if (
                current_config["license_level"] != "free"
                or len(current_config["license_code"]) > 0
            ):
                try:
                    # Retrieve config from Cloud
                    print("Retrieving config from Cloud")
                    post_url = requests.post(
                        current_config["api_server"] + "/api/config/sync",
                        json={
                            "id": current_config["email_address"],
                            "license": current_config["license_code"],
                        },
                    )
                    cloud_config = json.loads(post_url.text)["details"]
                    # Apply Cloud config if not license_validated
                    with open(
                        config_dir + "/all.json", "r+", encoding="UTF-8"
                    ) as config_file:
                        config_file_data = json.load(config_file)
                        for setting in cloud_config:
                            if setting != "license_validated":
                                config_file_data[setting] = cloud_config[setting]
                        config_file.seek(0)
                        config_file.write(json.dumps(config_file_data))
                        config_file.truncate()
                        logging.info("Updated local config from cloud")
                except Exception as error_message:
                    print("Failed to retrieve config: " + str(error_message))

        if len(threading.enumerate()) < 2:
            if not first_run:
                sg.Popup("Log your time!", font=font)
                logging.info("Time logging prompt acknowledged")
            notify_thread_manage = NotifyThread()
            notify_thread_manage.start()
            first_run = False

        # Check licensing
        if not first_run:
            # If not a free license, validate with api
            if (
                current_config["license_level"] != "free"
                or len(current_config["license_code"]) > 0
            ):
                licensing_check = json.loads(check_licensing())
                if licensing_check["status"] != "ok":
                    licensing_message = (
                        "Licensing issues detected, closing:\n"
                        + licensing_check["details"]
                    )
                    sg.Popup(licensing_message, font=font)
                    logging.info(licensing_message)
                    notify_thread_manage.stop()
                    notify_thread_manage.join()
                    break

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
                    logging.info("%s time logged", raw_event)
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
