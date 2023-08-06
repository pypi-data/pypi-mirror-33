import traceback
from typing import Dict, Any, List, Optional, Union

from django.template import Context, Template as DjangoTemplate
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.db import models

from .models import (
    Template as TemplateModel, Attachment, Letter as LetterModel,
    Log as LogModel
)
from .utils import to_str, to_list, default_language
from .const import LETTER_STATUSES, POSTIE_TEMPLATE_CONTEXTS
from .backends import CeleryEmailBackend, EmailBackend

__all__ = (
    'Letter',
    'Template'
)


class BaseEntity:
    """
    Base entity class.

    Attributes:
        model (models.Model): Entity model.
        object: Entity instance.
    """

    model = None  # type: models.Model

    def __init__(self, obj):
        self.object = obj


class Letter(BaseEntity):
    """
    Letter entity. Stores letter mailing logic.
    """

    model = LetterModel  #type: LetterModel

    @property
    def message(self) -> EmailMultiAlternatives:
        """
        Creates corresponding EmailMultiAlternatives letter.

        Returns:
            EmailMultiAlternatives
        """

        message = EmailMultiAlternatives(
            self.object.subject, self.object.plain, self.object.email_from,
            to_list(self.object.recipients)
        )

        if self.object.html:
            message.attach_alternative(self.object.html, "text/html")

        for attachment in self.object.attachments.all():
            message.attach_file(
                f'{settings.MEDIA_ROOT}/{attachment.attachment.name}'
            )

        return message

    @property
    def backend(self) -> Union[EmailBackend, CeleryEmailBackend]:
        if settings.POSTIE_INSTANT_SEND:
            return EmailBackend

        return CeleryEmailBackend

    def _send(self):
        """
        Actual sending method. Message is generated here and send using
        django's email backend specified in the settings.
        """

        try:
            self.message.send()
            is_failed = False
        except Exception as e:
            LogModel.objects.create(
                letter=self.object,
                message=str(e),
                traceback=traceback.format_exc()
            )
            is_failed = True

        if is_failed:
            self.set_failed()
        else:
            self.set_sent()

    def send(self, backend: Optional[CeleryEmailBackend]=None) -> None:
        """
        Sends an email letter using the corresponding UseCase class.
        If not backend specified SendMailUseCase is used.

        Args:
            backend (Optional[SendMailUseCase]):

        Returns:
            None
        """

        if not backend:
            backend = self.backend

        backend().send(self)

    def set_failed(self) -> None:
        """
        Sets the letter as a failed.

        Returns:
            None
        """

        self.object.status = LETTER_STATUSES.failed
        self.object.save()

    def set_sent(self) -> None:
        """
        Sets the letter a sent.

        Returns:
            None
        """

        self.object.status = LETTER_STATUSES.sent
        self.object.save()

    def add_attachment(self, file_name: str, attachment) -> None:
        """
        Adds attachment to a letter.

        Args:
            file_name (str): File name.
            attachment: File content.

        Returns:
            None
        """

        obj = Attachment(letter=self.object)
        obj.attachment.save(file_name, attachment, save=True)

    @classmethod
    def load_from_id(cls, pk: int) -> 'Letter':
        """
        Returns Letter entity loaded from DB with a given ID.

        Args:
            pk (int): LetterModel id.

        Returns:
            Letter: Letter entity instance.
        """

        orm_letter = LetterModel.objects.filter(pk=pk).not_sent().first()

        if not orm_letter:
            raise ValueError(
                _('Letter with id "{}" is not exists or already sent')
                .format(pk)
            )

        return Letter(orm_letter)


class Template(BaseEntity):
    """
    Template entity. Stores logic for a creating letter from a
    template.
    """

    model = TemplateModel  # type: TemplateModel

    @property
    def legend(self) -> str:
        """
        Returns prettified template legend.

        Returns:
            str: Template variable language.
        """

        legend = '\n'.join(
            f'{{{{ {key} }}}}: {value}'
            for key, value in
            POSTIE_TEMPLATE_CONTEXTS.get(self.object.event, {}).items()
        )

        return legend

    def set_language(self, language: str=None) -> None:
        """
        Changes object language.

        Args:
            language (str): Language to set.
        """

        if not language:
            language = default_language()

        if self.object.get_current_language() != language:
            if not self.object.has_translation(language):
                raise ValueError(
                    _('There is not translation for "{}" for {} template')
                    .format(language, self.object.name)
                )

            self.object.set_current_language(language, initialize=True)

    def render(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Renders template with a given context.

        Args:
            context (Dict[str, Any]): Template context.

        Returns:
            Dict[str, str]: Rendered template fields to use in letter.
        """

        subject = DjangoTemplate(self.object.subject).render(Context(context))
        html = DjangoTemplate(self.object.html).render(Context(context))
        plain = DjangoTemplate(self.object.plain).render(Context(context))

        return {
            'subject': subject,
            'html': html,
            'plain': plain
        }

    def new_letter(
            self,
            context: Dict[str, Any],
            recipients: List[str],
            email_from: Optional[str]=None,
            attachments: Optional[List]=None,
            language: Optional[str]=None
    ) -> Letter:
        """Creates new letter

        Args:
            context (Dict[str, Any]): Mail letter context.
            recipients (List[str]): Letter recipients.
            email_from (Optional[str]): Letter sender email address.
            attachments (Optional[List]): Letter attachments.
            language (Optional[str]): Letter language to send.

        Returns:
            Letter: New Letter entity
        """

        self.set_language(language)

        rendered_fields = self.render(context)

        if not email_from:
            email_from = settings.DEFAULT_FROM_EMAIL

        letter = LetterModel.objects.create(
            subject=rendered_fields['subject'],
            html=rendered_fields['html'],
            plain=rendered_fields['plain'],
            email_from=email_from,
            event=self.object.event,
            recipients=to_str(recipients),
            language=language
        )
        letter_entity = Letter(letter)

        if attachments:
            for attachment in attachments:
                letter_entity.add_attachment(
                    *list(attachment.items())[0]
                )

        return letter_entity

    @classmethod
    def from_event(cls, event: str) -> 'Template':
        """
        Returns Template entity for the given event.

        Args:
            event (str): Template event to search.

        Returns:
            Template: Template entity instance.
        """

        template = TemplateModel.objects.filter(event=event).first()

        if not template:
            raise ValueError(_('No MailTemplate for "{}" event').format(event))

        return cls(template)
