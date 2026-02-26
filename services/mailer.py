from typing import Any, Dict, List, Optional
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType

from core.mail import mail_conf

class Mailer:
    def __init__(self) -> None:
        self.fm = FastMail(mail_conf)

    async def send_html(
        self,
        subject: str,
        recipients: List[str],
        html: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html,
            subtype=MessageType.html,
        )
        if background_tasks:
            background_tasks.add_task(self.fm.send_message, message)
        else:
            await self.fm.send_message(message)

    async def send_template(
        self,
        subject: str,
        recipients: List[str],
        template_name: str,
        context: Dict[str, Any],
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> None:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=context,
            subtype=MessageType.html,
        )
        if background_tasks:
            background_tasks.add_task(self.fm.send_message, message, template_name=template_name)
        else:
            await self.fm.send_message(message, template_name=template_name)