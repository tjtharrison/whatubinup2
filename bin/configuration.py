""" Module to get configuration from local config """
import json
import logging
from os.path import expanduser

home_dir = expanduser("~") + "/whatubinup2/"


def get_config():
    """Function to get configuration from local config"""
    try:
        with open(home_dir + "config/all.json", encoding="utf-8") as config:
            config = json.load(config)
    except FileNotFoundError:
        logging.info("Generating config file on first run")
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
        logging.info("Default config applied!")
        config = default_config
    return json.dumps(config)
