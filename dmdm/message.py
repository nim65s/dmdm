"""Extend django/core/mail/message.py."""

from email import encoders as Encoders
from email.mime.base import MIMEBase
import mimetypes
from django.core.mail.message import (
    EmailMultiAlternatives,
    DEFAULT_ATTACHMENT_MIME_TYPE,
)


class EmailMultiAlternativesInline(EmailMultiAlternatives):
    """Extend EmailMultiAlternative with inline attachments."""

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
        self.inlines = []

    def inline(self, filename=None, content=None, mimetype=None):
        """
        Inline a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.
        """
        mimetype = (
            mimetype
            or mimetypes.guess_type(filename)[0]
            or DEFAULT_ATTACHMENT_MIME_TYPE
        )
        self.inlines.append((filename, content, mimetype))

    def _create_message(self, msg):
        msg = super()._create_message(msg)
        return self._create_inlines(msg)

    def _create_inlines(self, msg):
        for inline in self.inlines:
            msg.attach(self._create_inline(*inline))
        return msg

    def _create_inline(self, filename, content, mimetype=None):
        inline = self._create_mime_inline(content, mimetype)
        if filename:
            try:
                filename.encode("ascii")
            except UnicodeEncodeError:
                filename = ("utf-8", "", filename)
            inline.add_header("Content-Disposition", "inline", filename=filename)
        return inline

    def _create_mime_inline(self, content, mimetype):
        basetype, subtype = mimetype.split("/", 1)
        inline = MIMEBase(basetype, subtype)
        inline.set_payload(content)
        Encoders.encode_base64(inline)
        return inline
