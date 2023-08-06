from typing import Dict, Any, List, Optional

from .entities import Template, Letter

__all__ = (
    'send_mail',
)


def send_mail(
        event: str, recipients: List[str], context: Dict[Any, Any],
        from_email: Optional[str]=None, attachments: Optional[List[Dict]]=None,
        language: str=None, backend=None
    ) -> Letter:
    """Shortcut to send email.

    Args:
        event (str): Event to send email. Used to get template.
        recipients (List[str]): Recipients email list.
        context (Dict[any, any]): Email context.
        from_email (Optional[str]): Sender email address.
        attachments (Optional[List[str]]): Letter attachments.
        language (str): Letter language.

    Raises:
        ValueError: No template found for given "event"

    Returns:
        Letter: New Letter entity.
    """

    if attachments is None:
        attachments = []

    template = Template.from_event(event)
    letter = template.new_letter(
        context=context,
        recipients=recipients,
        email_from=from_email,
        attachments=attachments,
        language=language
    )

    letter.send(backend)

    return letter
