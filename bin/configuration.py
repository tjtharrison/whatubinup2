import json
from os.path import exists, expanduser

home_dir = expanduser("~") + "/"


def get_config():
    """Function to get or generate app config"""
    with open(home_dir + "whatubinup2/config/all.json", encoding="utf-8") as config:
        config = json.load(config)
    return json.dumps(config)
