import traceback

from celery import shared_task

from .models import Log

__all__ = (
    'send_letter'
)


@shared_task
def send_letter(letter_id: int):
    from .entities import Letter

    letter = Letter.load_from_id(letter_id)

    try:
        letter.message.send()
        is_failed = False
    except Exception as e:
        Log.objects.create(
            letter=letter.object,
            message=str(e),
            traceback=traceback.format_exc()
        )
        is_failed = True

    if is_failed:
        letter.set_failed()
    else:
        letter.set_sent()

    return letter
