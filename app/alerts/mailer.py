import os
import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", "OsijekHousing <noreply@osijekhousing.local>")

    if not user or not password:
        print(f"[TEST EMAIL] Za: {to_email} | Naslov: {subject}\n{body}", flush = True) #flush = True je bitan da se tekst odma ispise u terminalu/logovima 
        return

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.add_alternative(body, subtype="html")

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)