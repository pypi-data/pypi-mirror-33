from django.db import models

from .const import LETTER_STATUSES

__all__ = (
    'LetterQuerySet',
)


class LetterQuerySet(models.QuerySet):
    def not_sent(self) -> models.QuerySet:
        """
        Filters not sent letters.
        
        Returns:
            models.QuerySet: not sent letters.
        """
        return self.exclude(status=LETTER_STATUSES.sent)

    def sent(self) -> models.QuerySet:
        """
        Filters sent letters
        
        Returns:
            models.QuerySet: sent letters.
        """
        return self.filter(status=LETTER_STATUSES.sent)
