import os
import smtplib
from email.mime.text import MIMEText

def send_monthly_email():
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    user = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    to_addr = os.environ["EMAIL_TO"]

    subject = "Sua mensagem mensal"
    body = "Olá! Esta é a sua mensagem agendada para todo dia 20."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)
        print("E-mail enviado com sucesso!")

if __name__ == "__main__":
    send_monthly_email()
