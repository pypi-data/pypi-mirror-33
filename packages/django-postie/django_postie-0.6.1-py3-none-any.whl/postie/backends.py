from typing import TYPE_CHECKING

from celery.result import AsyncResult

from .tasks import send_letter

if TYPE_CHECKING:
    from .entities import Letter

__all__ = (
    'BaseEmailBackend',
    'EmailBackend',
    'CeleryEmailBackend',
)


class BaseEmailBackend():
    def send(self, letter: 'Letter'):
        return NotImplemented


class EmailBackend(BaseEmailBackend):
    def send(self, letter: 'Letter') -> 'Letter':
        return letter._send()


class CeleryEmailBackend(BaseEmailBackend):
    """
    Send email use case. Used to send email, duh.
    """

    def send(self, letter: 'Letter') -> AsyncResult:
        """
        Calls `send_letter` task to send email.

        Args:
            letter (Optional[Letter]): Letter entity instance.

        Returns:
            Optional[Letter]: Letter instance or None
        """
        return send_letter.delay(letter.object.id)
