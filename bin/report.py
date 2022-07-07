""" Module for creating and retrieving reports """
import json
import logging
from datetime import date
from os.path import expanduser

import PySimpleGUI as sg

home_dir = expanduser("~") + "/whatubinup2/"
today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)


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
