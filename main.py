""" Simple UI for Time logging """
import json
import logging
import os
import time
from datetime import date
from os.path import exists, expanduser
from threading import Thread

import PySimpleGUI as sg

from bin import configuration, init, notify, report, settings

home_dir = expanduser("~") + "/whatubinup2/"

today = date.today()
today_date = today.strftime("%y-%m-%d")
font = ("Open Sans", 15)

sg.theme("DarkTeal9")

# Setup dirs
init.setup_dirs()

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

if __name__ == "__main__":
    main_window = sg.Window(
        "What U bin up 2", main_layout, keep_on_top=True, size=(180, 250)
    )
    start_time = time.time()
    START_NOTIFIER = True

    while True:
        today_report = json.loads(report.get_report())
        current_config = json.loads(configuration.get_config())
        if START_NOTIFIER is True:
            START_NOTIFIER = False
            T = Thread(target=notify.do_notify, args=(start_time,))
            T.start()

        if exists(home_dir + "tmp/do_notify"):
            sg.Popup("Log your time!", font=font)
            os.remove(home_dir + "tmp/do_notify")
        working_hours = current_config["total_hours"]["value"]
        event, values = main_window.read(timeout=2)
        # Avoiding race condition on first launch
        try:
            HOURS_SPENT = (
                today_report["meetings"]
                + today_report["planned_dev"]
                + today_report["unplanned_dev"]
            )
        except TypeError:
            logging.info("No hours reported yet")
            HOURS_SPENT = 0
        main_window["current_total"].update(
            "Total logged: " + str(HOURS_SPENT) + "/" + str(working_hours)
        )

        TIME_LOGGED = False
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        if event == "Report":
            report.show_report()
        if event == "Settings":
            settings.show_settings()
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
            with open(
                home_dir + "reports/" + today_date + ".json",
                "w",
                encoding="UTF-8",
            ) as report_file:
                report_file.write(json.dumps(today_report))
                report_file.close()
            sg.PopupNoButtons(
                "New total for " + event + " is " + str(NEW_TOTAL),
                font=font,
                auto_close_duration=1,
                auto_close=True,
            )


main_window.close()
