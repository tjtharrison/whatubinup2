""" Simple UI for Time logging """
import json
import logging
from datetime import date

import PySimpleGUI as sg

today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)

TOTAL_MEETINGS = 0
TOTAL_SUPPORT = 0
TOTAL_DEV = 0
sg.theme("DarkTeal9")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./logs/application_" + today_date + ".log"),
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

# Generate config if not present
def get_config():
    """Function to get or generate app config"""
    try:
        with open("./config/all.json", encoding="utf-8") as config:
            logging.debug("Loading config")
            config = json.load(config)
    except:
        logging.info("Generating config file on first run")
        with open("./config/all.json", "w", encoding="UTF-8") as config_file:
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
            config_file.write(default_config)
            config_file.close()
        logging.info("Default config applied!")
        config = default_config
    return json.dumps(config)


# Open the daily report
def get_report():
    """App to get or generate todays report"""
    try:
        with open("./reports/" + today_date + ".json", encoding="utf-8") as report:
            logging.debug("Loading report")
            report = json.load(report)
    except:
        logging.info("Generating report file on first run for today")
        with open("./reports/" + today_date + ".json", "w", encoding="UTF-8") as report_file:
            report_skeleton = json.dumps(
                {"meetings": 0, "planned_dev": 0, "unplanned_dev": 0}
            )
            report_file.write(report_skeleton)
            report_file.close()
        logging.info("Default report_skeleton applied to report!")
        report = report_skeleton
    return json.dumps(report)


def show_report():
    """Popup modal with current time logging stats"""
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
        with open("./config/all.json", "w", encoding="UTF-8") as config_file:
            config_file.write(new_config)
            config_file.close()
        logging.info("New settings applied: %s", new_config )
    settings_window.close()


if __name__ == "__main__":
    main_window = sg.Window("What U bin up 2", main_layout, keep_on_top=True)
    while True:
        today_report = json.loads(get_report())
        current_config = json.loads(get_config())
        working_hours = current_config["total_hours"]["value"]

        hours_spent = (
            today_report["meetings"]
            + today_report["planned_dev"]
            + today_report["unplanned_dev"]
        )
        event, values = main_window.read(timeout=2)
        main_window["current_total"].update(
            "Total logged: " + str(hours_spent) + "/" + str(working_hours)
        )

        TIME_LOGGED = False
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        if event == "Report":
            show_report()
        if event == "Settings":
            show_settings()
        if event == "Meetings":
            today_report["meetings"] = today_report["meetings"] + 1
            NEW_TOTAL = today_report["meetings"]
            logging.info("Meeting time logged")
            TIME_LOGGED = True
        if event == "Planned Dev":
            today_report["planned_dev"] = today_report["planned_dev"] + 1
            NEW_TOTAL = today_report["planned_dev"]
            logging.info("Planned Dev time logged")
            TIME_LOGGED = True
        if event == "Unplanned Dev":
            today_report["unplanned_dev"] = today_report["unplanned_dev"] + 1
            NEW_TOTAL = today_report["unplanned_dev"]
            logging.info("Unplanned Dev time logged")
            TIME_LOGGED = True
        if TIME_LOGGED is True:
            with open("./reports/" + today_date + ".json", "w", encoding="UTF-8") as report_file:
                report_file.write(json.dumps(today_report))
                report_file.close()
            sg.PopupNoButtons(
                "New total for " + event + " is " + str(NEW_TOTAL),
                font=font,
                auto_close_duration=1,
                auto_close=True,
            )

main_window.close()
