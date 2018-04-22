from django.core.mail import EmailMessage

from mdmail.api import EmailContent


class MarkdownMailMessage(EmailMessage):
    pass


class DjangoEmailContent(EmailContent):
    pass
