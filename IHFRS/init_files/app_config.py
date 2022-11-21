# Initial settings for our custom application.
# This app creates a .ini file from which the IHFRS application reads its settings.
# This file will be mostly unused other than for development, once the INI file has been made.
from configparser import ConfigParser

config = ConfigParser()

# Settings for Homekit Process.
config["HomekitSettings"] = {
    "port": "33864"
}

# Settings for TCAM Process.
config["TCAMSettings"] = {
    "tempAlertValue": "100",
}

# Creates INI file.
with open('config.ini', 'w') as conf:
    config.write(conf)

