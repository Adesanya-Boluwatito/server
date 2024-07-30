from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import random

def generate_otp():
    otp_secret = random.randint(1000, 9999)
    return otp_secret

OTP = None

def send_OTP(mail):
    USERNAME = "adesanyaboluwatito69@gmail.com"
    PASSWORD = "pypx fygu ouph bdoa"
    global OTP

    OTP = generate_otp()

    with SMTP(host="smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=USERNAME, password=PASSWORD)

        subject = "Your OTP"
        body = f"This is your OTP: {OTP}, please do not disclose this to anyone"

        msg = MIMEMultipart()
        msg['From'] = USERNAME
        msg['To'] = mail
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        connection.sendmail(from_addr=USERNAME,
                            to_addrs=mail,
                            msg=msg.as_string()
                            )

def verify_otp(entered_otp):
    global OTP
    return str(OTP) == entered_otp