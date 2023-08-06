from typing import Dict, Any, List, Optional

from .entities import Template, Letter

__all__ = (
    'send_mail',
)


def send_mail(
        event: str, recipients: List[str], context: Dict[Any, Any],
        from_email: Optional[str]=None, attachments: Optional[List[str]]=None
    ) -> Letter:
    """Shortcut to send email.

    Args:
        event (str): Event to send email. Used to get template.
        recipients (List[str]): Recipients email list.
        context (Dict[any, any]): Email context.
        from_email (Optional[str]): Sender email address.
        attachments (Optional[List[str]]): Letter attachments
        
    Raises:
        ValueError: No template found for given "event"
    """

    if attachments is None:
        attachments = []

    template = Template.from_event(event)
    letter = template.new_letter(
        context, recipients, from_email, attachments
    )

    letter.send()
    
    return letter
