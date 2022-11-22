# Initial settings for our custom application.
# This app creates a .ini file from which the IHFRS application reads its settings.
# This file will be mostly unused other than for development, once the INI file has been made.
from configparser import ConfigParser

config = ConfigParser()

config["SMSEnable"] = {
    "SMSEnabled": False
}

# Settings for Twilio.
config["TwilioSettings"] = {
    "accountSID": "AC31331230a20f77ec7624c5e38311cea6",
    "authToken": "7a93ef0412569dcc84ea0289247c6e9f",
    "recipientPhone": "+19417042631",
    "sendingPhone": "+16815324346",
}

# Settings for Homekit Process.
config["HomekitSettings"] = {
    "port": "34985"
}

# Settings for TCAM Process.
config["TCAMSettings"] = {
    "tempAlertValue": "100",
}

# Creates INI file.
with open('config.ini', 'w') as conf:
    config.write(conf)

