from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from notifications.config import mail_settings


async def send_email_smtp(
    recipients: list[str],
    subject: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{mail_settings.mail_from_name} <{mail_settings.mail_from}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    await aiosmtplib.send(
        msg,
        hostname=mail_settings.smtp_host,
        port=mail_settings.smtp_port,
        username=mail_settings.smtp_user,
        password=mail_settings.smtp_password,
        start_tls=mail_settings.smtp_use_tls,
    )