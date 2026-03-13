import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import aiosmtplib

from notifications.config import mail_settings

logger = logging.getLogger(__name__)


async def send_email_smtp(
    recipients: List[str],
    subject: str,
    html_body: str,
) -> None:
    from_email = mail_settings.mail_from
    from_name = mail_settings.mail_from_name
    smtp_host = mail_settings.smtp_host
    smtp_port = mail_settings.smtp_port
    smtp_user = mail_settings.smtp_user
    smtp_use_tls = mail_settings.smtp_use_tls

    logger.warning(
        "[smtp_client.send_email_smtp] preparando envío | host=%s port=%s tls=%s user=%s from=%s recipients=%s subject=%s",
        smtp_host,
        smtp_port,
        smtp_use_tls,
        smtp_user,
        from_email,
        recipients,
        subject,
    )

    if not recipients:
        logger.warning("[smtp_client.send_email_smtp] recipients vacío, no se puede enviar")
        raise ValueError("La lista de recipients está vacía")

    if not from_email:
        logger.warning("[smtp_client.send_email_smtp] MAIL_FROM no está configurado")
        raise ValueError("MAIL_FROM no está configurado")

    msg = MIMEMultipart("alternative")
    msg["From"] = "{0} <{1}>".format(from_name, from_email)
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    logger.warning(
        "[smtp_client.send_email_smtp] intentando envío SMTP | from=%s to=%s subject=%s body_len=%s",
        from_email,
        recipients,
        subject,
        len(html_body or ""),
    )

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=mail_settings.smtp_password,
            start_tls=smtp_use_tls,
        )

        logger.warning(
            "[smtp_client.send_email_smtp] envío SMTP aceptado | from=%s to=%s subject=%s",
            from_email,
            recipients,
            subject,
        )

    except Exception as exc:
        logger.warning(
            "[smtp_client.send_email_smtp] fallo en envío SMTP | from=%s to=%s subject=%s error=%r",
            from_email,
            recipients,
            subject,
            exc,
        )
        raise