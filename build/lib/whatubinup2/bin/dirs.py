""" Module to initialise directories """
import json
import os
from datetime import date
from os.path import exists, expanduser

today = date.today()
today_date = today.strftime("%y-%m-%d")

home_dir = expanduser("~") + "/whatubinup2/"


def setup_dirs():
    """Function to initialise directories"""
    # Setup dir structure
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
        with open(home_dir + "config/all.json", "w", encoding="UTF-8") as config_file:
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
        with open(
            home_dir + "reports/" + today_date + ".json",
            "w",
            encoding="UTF-8",
        ) as report_file:
            report_skeleton = json.dumps(
                {"meetings": 0, "planned_dev": 0, "unplanned_dev": 0}
            )
            report_file.write(report_skeleton)
            report_file.close()
