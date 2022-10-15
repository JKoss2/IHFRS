from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
from twilio.rest import Client
import RPi. GPIO as GPIO

def notification(bodyMessage, subject):

    port= 587
    timeout = 15
    smtpServer = 'smtp.gmail.com'
    account_sid = "AC31331230a20f77ec7624c5e38311cea6"
    # Your Auth Token from twilio.com/console
    auth_token  = "7a93ef0412569dcc84ea0289247c6e9f"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    to="+15614528645",
    from_="+16815324346",
    body=bodyMessage)
    print(message.sid)
    with smtplib.SMTP(host=smtpServer, port=port,timeout=timeout) as server:
                            context = ssl._create_unverified_context()
                            server.starttls(context=context)
                            fromAddress = 'raspigroup15@gmail.com'
                            password = 'quqtojujdlqxszrr'
                            server.login(fromAddress, password)  # Your email address & password here
                            htmlMessage = bodyMessage
                            message = MIMEMultipart("alternative")
                            message["Subject"] = subject
                            message["From"] = fromAddress
                            message["To"] = 'sergeykunaev94@gmail.com'
                            part1 = MIMEText(htmlMessage, 'plain')
                            message.attach(part1)
                            if htmlMessage is not None:
                                    part2 = MIMEText(htmlMessage, "html")
                                    message.attach(part2)
                                    recipients='sergeykunaev94@gmail.com'
                                    server.sendmail(fromAddress,recipients,message.as_string())
                                    