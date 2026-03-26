"""Main source file."""

from typing import Dict, List, Optional, Tuple, Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.encoding import force_bytes
from django.core.mail.backends.base import BaseEmailBackend
from django.http import HttpRequest
from django.template.loader import get_template
from nmdmail.api import EmailContent


class DMDM(EmailMultiAlternatives):
    def __init__(
        self,
        *args,
        html: str | None = None,
        inline_images: dict[str, bytes] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if html is None:
            raise AttributeError("you probably need html here")
        self.attach_alternative(html, "text/html")
        self.inline_images: dict[str, bytes] = inline_images or {}

    def _add_bodies(self, msg):
        msg.make_alternative()
        encoding = self.encoding or settings.DEFAULT_CHARSET
        for alternative in self.alternatives:
            maintype, subtype = alternative.mimetype.split("/", 1)
            content = alternative.content
            if maintype == "text":
                if isinstance(content, bytes):
                    content = content.decode()
                msg.add_alternative(content, subtype=subtype, charset=encoding)
            else:
                content = force_bytes(content, encoding=encoding, strings_only=True)
                msg.add_alternative(content, maintype=maintype, subtype=subtype)

        for filename, data in self.inline_images:
            msg.get_payload()[-1].add_related(data, "image", "png", cid=filename)

        return msg


def send_mail(
    subject: str,
    message: str,
    from_email: str,
    recipient_list: List[str],
    context: Optional[Dict] = None,
    request: Optional[HttpRequest] = None,
    fail_silently: bool = False,
    css: Optional[str] = None,
    image_root: str = ".",
    auth_user: Optional[str] = None,
    auth_password: Optional[str] = None,
    connection: Optional[BaseEmailBackend] = None,
    reply_to: Optional[List[str]] = None,
    attachments: Optional[List[Tuple[str, Any, str]]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> int:
    """Drop in replacement for django.core.email.send_mail."""
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    if context is not None:
        message = get_template(message).render(context, request)
    content = EmailContent(message, css=css, image_root=image_root)
    mail = DMDM(
        subject=subject,
        body=content.text,
        from_email=from_email,
        to=recipient_list,
        connection=connection,
        reply_to=reply_to,
        headers=headers,
        html=content.html,
        inline_images=content.inline_images,
    )

    if attachments:
        for filename, data, mimetype in attachments:
            mail.attach(filename, data, mimetype)

    return mail.send()
