import yaml
import sys
import os
from os.path import expanduser


def _get_config_location():
    home = expanduser("~")
    return "{}/.dli/config.yaml".format(home)


def _load_config():
    _config_location = _get_config_location()

    if os.path.isfile(_config_location):
        try:
            with open(_config_location, 'r') as stream:
                config = yaml.load(stream)
            return config
        except yaml.YAMLError as exc:
            print("Error: {}.".format(exc))
            return None
    else:
        return None


def get_config():
    config = _load_config()

    if not config:
        print("DLI not configured!")
        print("Please run [dli configure] to setup the environment")
        sys.exit(1)
    else:
        return config
