from django.conf import settings

from .shortcuts import send_mail

__all__ = (
    'MailSendFormMixin',
)


class MailSendFormMixin:
    """
    Form mixin that sends email after form saving

    Attributes:
        email_template (str): Email template to use in sending.
            One of the choices in MailTemplate's event field
    """

    email_template = None  # type: str

    def get_email_context(self):
        """
        Returns email context to use in rendering.

        Returns:
            dict: email context.
        """
        return {
            key: str(value) for key, value in self.cleaned_data.items()
        }

    def get_email_template(self):
        """
        Returns email template to render.

        Returns:
            str: email template name
        """
        return self.email_template

    def get_email_recipients(self):
        """
        Return recipients to send email

        Returns:
            list: emails to send letter
        """

        raise NotImplementedError()
    
    def get_email_sender(self) -> str:
        """
        Returns sender email address
        
        Returns:
            str: sender email address
        """
        
        return settings.DEFAULT_FROM_EMAIL

    def send_email(self):
        """
        Sends email.
        """
        
        send_mail(
            self.get_email_template(),
            self.get_email_recipients(),
            self.get_email_context(),
            self.get_email_sender()
        )

    def save(self, *args, **kwargs):
        """
        Overrides default save to send email after saving.
        """
        response = None

        if hasattr(super(), 'save'):
            response = super().save(*args, **kwargs)

        self.send_email()

        return response
