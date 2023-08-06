from celery import shared_task

__all__ = (
    'send_letter'
)


@shared_task
def send_letter(letter_id: int):
    """
    Right now this task is used to send letter. It's the only
    difference between `EmailBackend` and `CeleryEmailBackend` in how
    they send emails

    Args:
        letter_id (int): Letter object id

    """
    from .entities import Letter

    letter = Letter.load_from_id(letter_id)
    letter._send()
