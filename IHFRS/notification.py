from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
from twilio.rest import Client
from configparser import ConfigParser


def notification(body_message, subject):
    # Setup Preference Reader
    config_reader = ConfigParser()
    config_reader.read("config.ini")

    twilio_settings = config_reader["TwilioSettings"]
    tw_account_sid = twilio_settings["accountSID"]
    tw_auth_token = twilio_settings["authToken"]
    tw_recipient_phone = twilio_settings["recipientPhone"]
    tw_sending_phone = twilio_settings["sendingPhone"]

    # Twilio SMS Notifications
    account_sid = tw_account_sid
    auth_token = tw_auth_token
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=tw_recipient_phone,
        from_=tw_sending_phone,
        body=body_message)
    print(message.sid)

    pass

    # Email Notifications
    # port = 587
    # timeout = 15
    # smtpServer = 'smtp.gmail.com'
    # with smtplib.SMTP(host=smtpServer, port=port,timeout=timeout) as server:
    #     context = ssl._create_unverified_context()
    #     server.starttls(context=context)
    #     fromAddress = 'raspigroup15@gmail.com'
    #     password = 'quqtojujdlqxszrr'
    #     server.login(fromAddress, password)  # Your email address & password here
    #     htmlMessage = body_message
    #     message = MIMEMultipart("alternative")
    #     message["Subject"] = subject
    #     message["From"] = fromAddress
    #     message["To"] = 'sergeykunaev94@gmail.com'
    #     part1 = MIMEText(htmlMessage, 'plain')
    #     message.attach(part1)
    #     if htmlMessage is not None:
    #         part2 = MIMEText(htmlMessage, "html")
    #         message.attach(part2)
    #         recipients='sergeykunaev94@gmail.com'
    #         server.sendmail(fromAddress,recipients,message.as_string())
