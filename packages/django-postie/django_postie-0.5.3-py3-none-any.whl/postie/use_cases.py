from django.conf import settings

from .tasks import send_letter

__all__ = (
    'SendMailUseCase',
)


class SendMailUseCase:
    """
    Send email use case. Used to send email, duh.
    """

    def execute(self, letter) -> 'Optional[Letter]':
        """
        Calls `send_letter` task to send email.

        Args:
            letter (Optional[Letter]): Letter entity instance.

        Returns:
            Optional[Letter]: Letter instance or None
        """
        if getattr(settings, 'POSTIE_INSTANT_SEND', True):
            return send_letter(letter.object.id)
        else:
            send_letter.delay(letter.object.id)

            return None
