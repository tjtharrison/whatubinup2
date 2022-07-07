""" Module to get settings from local config """
import json
import logging
from datetime import date
from os.path import expanduser

import PySimpleGUI as sg
from bin import configuration

home_dir = expanduser("~") + "/whatubinup2/"
today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)


def show_settings():
    """Popup modal with current settings"""
    logging.info("Settings opened")
    config = json.loads(configuration.get_config())
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
