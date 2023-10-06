import smtplib
import ssl

from email.mime.text import MIMEText

from core.config import settings
from core.exceptions import HTTP_500


def mail_service(mail_to: str, subject: str, content: str) -> None:
    port = settings.smtp_port  # For starttls
    smtp_server = settings.smtp_server
    sender_email = settings.email
    receiver_email = mail_to
    password = settings.app_pw
    message = MIMEText(content, _subtype='plain')
    message['Subject'] = subject

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        raise HTTP_500(
            msg="There was some error sending email..."
        )
