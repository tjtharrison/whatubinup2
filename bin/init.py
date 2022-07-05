import json
import os
from datetime import date
from os.path import exists, expanduser

today = date.today()
today_date = today.strftime("%y-%m-%d")

home_dir = expanduser("~") + "/"


def setup_dirs():
    # Setup dir structure
    if not exists(home_dir + "whatubinup2"):
        dirs = [
            home_dir + "whatubinup2",
            home_dir + "whatubinup2/tmp",
            home_dir + "whatubinup2/config",
            home_dir + "whatubinup2/reports",
            home_dir + "whatubinup2/logs",
        ]
        for dir in dirs:
            os.mkdir(dir)
        with open(
            home_dir + "whatubinup2/config/all.json", "w", encoding="UTF-8"
        ) as config_file:
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
            home_dir + "whatubinup2/reports/" + today_date + ".json",
            "w",
            encoding="UTF-8",
        ) as report_file:
            report_skeleton = json.dumps(
                {"meetings": 0, "planned_dev": 0, "unplanned_dev": 0}
            )
            report_file.write(report_skeleton)
            report_file.close()
