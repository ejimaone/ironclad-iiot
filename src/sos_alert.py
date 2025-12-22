import os
import smtplib
from email.mime.text import MIMEText

def get_cred(name):
    cred_dir = os.getenv("CREDENTIALS_DIRECTORY")
    if not cred_dir:
        return None
    try:
        with open(os.path.join(cred_dir, name), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

USER = os.getenv("MYEMAIL")
PASS = get_cred("MYSECRET")

def send_alert(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = USER
    msg["To"] = to
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(USER, PASS)
        server.sendmail(USER, to, msg.as_string())

# Usage
send_alert(
    to="RECIEVER@gmail.com",
    subject="IronClad Alert: Service Failed",
    body="The telemetry service has crashed 5 times."
)