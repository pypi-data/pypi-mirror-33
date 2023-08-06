from django.conf import settings

from .tasks import send_letter

__all__ = (
    'SendMailUseCase',
)


class SendMailUseCase:
    
    def execute(self, letter):
        if getattr(settings, 'MAIL_INSTANT_SEND', True):
            send_letter(letter.object.id)
        else:
            send_letter.delay(letter.object.id)
    