import os.path
import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings
from core.exceptions import HTTP_500


def mail_service(mail_to: str, subject: str, content: str, file_path: str = None) -> None:
    port = settings.smtp_port  # For starttls
    smtp_server = settings.smtp_server
    sender_email = settings.email
    receiver_email = mail_to
    password = settings.app_pw

    # Creating Multipart message and headers
    message = MIMEMultipart()
    message['Subject'] = subject
    message.attach(MIMEText(content, _subtype='plain'))

    # Open file in binary mode
    if file_path is not None:
        with open(file_path, "rb") as attachment:
            # Below line adds file as application/octet_stream
            part = MIMEBase("application", "octet_stream")
            part.set_payload(attachment.read())

        # Encoding file in ASCII characters for sending emails
        encoders.encode_base64(part)

        # header as attachment
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(file_path)}"
        )

        message.attach(part)

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
        ) from e
