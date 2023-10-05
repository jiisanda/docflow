from email.mime.text import MIMEText
from smtplib import SMTP_SSL as SMTP
from typing import Dict, Tuple, Union

from core.config import settings
from core.exceptions import HTTP_500


def mail_service(mail_to: str, subject: str, content: str) -> Union[Dict[str, Tuple[int, bytes]], Exception]:
    try:
        text_subtype = 'plain'
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subject
        msg['From'] = settings.email

        conn = SMTP(settings.smtp_server, settings.smtp_port)
        conn.set_debuglevel(False)
        conn.login(settings.email, settings.pw)
        try:
            return conn.sendmail(from_addr=settings.email, to_addrs=mail_to, msg=msg.as_string())
        finally:
            conn.quit()

    except Exception as e:
        raise HTTP_500(
            msg="There was some error sending email..."
        )
