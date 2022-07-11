""" Contains scripts for window displays """
import json
import logging
import os
from os.path import expanduser

import file_ops
import PySimpleGUI as sg

home_dir = expanduser("~") + "/whatubinup2/"
reports_dir = home_dir + "reports/"
config_dir = home_dir + "config/"
tmp_dir = home_dir + "tmp/"
logs_dir = home_dir + "logs/"

font = ("Open Sans", 15)
big_font = ("Open Sans", 25)


def show_report():
    """Popup modal with current time logging stats"""
    logging.info("Report opened")

    # Get newest files in dir
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
        [
            [
                sg.Text(
                    time_bin + ": " + str(json.loads(file_ops.get_report())[time_bin]),
                    font=font,
                )
            ]
            for time_bin in json.loads(file_ops.get_report())
        ],
        [sg.Frame("Historic Reports", historic_report_frame, font=font)],
    ]
    report_window = sg.Window(
        "Time Report", report_layout, use_default_focus=False, finalize=True
    )
    report_window.read()
    report_window.close()


def show_settings():
    """Popup modal with current settings"""
    logging.info("Settings opened")
    config = json.loads(file_ops.get_config())
    settings_layout = [
        [sg.Text("Settings", font=font)],
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
            for time_bin in json.loads(file_ops.get_bins())["time_bins"]
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
            for edit_bin in json.loads(file_ops.get_bins())["time_bins"]:
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
            for del_bin in json.loads(file_ops.get_bins())["time_bins"]:
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
