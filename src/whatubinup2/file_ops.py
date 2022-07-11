""" Contains functions that interact with files """
import json
import logging
import os
from datetime import date
from os.path import exists, expanduser

home_dir = expanduser("~") + "/whatubinup2/"
reports_dir = home_dir + "reports/"
config_dir = home_dir + "config/"
tmp_dir = home_dir + "tmp/"
logs_dir = home_dir + "logs/"
today = date.today()
today_date = today.strftime("%y-%m-%d")

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


def check_for_dir(full_dir):
    """Function to create missing directories"""
    if not exists(full_dir):
        logging.info("%s dir does not exist, recreating..", full_dir)
        os.mkdir(full_dir)
        logging.info("%s dir created", full_dir)


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
