# Initial settings for our custom application.
# This app creates a .ini file from which the IHFRS application reads its settings.
# This file will be mostly unused other than for development, once the INI file has been made.
from configparser import ConfigParser

config = ConfigParser()

# These settings are used when device is "Factory Reset".
config["FACTORY_DEFAULT"] = {
    "smokeSensitivity": "20",
    "tempLimit1": "60",
    "tempLimit2": "100"

}

# Used when "Default" settings are called.
config["DEFAULT"] = {
    "smokeSensitivity": "20",
    "tempLimit1": "60",
    "tempLimit2": "100"

}

# Creates INI file.
with open('config.ini', 'w') as conf:
    config.write(conf)

# TODO: Add all settings and appropriate values.
