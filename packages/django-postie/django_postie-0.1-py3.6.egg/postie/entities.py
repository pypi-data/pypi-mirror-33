from typing import Dict, Any, List

from django.template import Context, Template as DjangoTemplate
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.files import File
from django.template.defaultfilters import striptags
from django.utils.translation import ugettext_lazy as _
from django.db import models

from .models import (
    Template as TemplateModel, Attachment, Letter as LetterModel
)
from .utils import encode_list, decode_list
from .const import LETTER_STATUSES, POSTIE_TEMPLATE_CONTEXTS
from .use_cases import SendMailUseCase

__all__ = (
    'Letter',
    'Template'
)


class BaseEntity:
    model = None  # type: models.Model
    
    def __init__(self, obj):
        self.object = obj


class Letter(BaseEntity):
    model = LetterModel
    
    @property
    def message(self) -> EmailMultiAlternatives:
        message = EmailMultiAlternatives(
            self.object.subject, self.object.plain, self.object.email_from,
            decode_list(self.object.recipients)
        )
    
        message.attach_alternative(self.object.html, "text/html")
    
        for attachment in self.object.attachments.all():
            message.attach_file(
                f'{settings.MEDIA_ROOT}/{attachment.attachment.name}'
            )
        
        return message
            
    def send(self, use_case=None):
        if not use_case:
            use_case = SendMailUseCase
            
        use_case().execute(self)
        
    def set_failed(self):
        self.object.status = LETTER_STATUSES.failed
        self.object.save()
        
    def set_sent(self):
        self.object.status = LETTER_STATUSES.sent
        self.object.save()
        
    def add_attachment(self, attachment):
        obj = Attachment(letter=self.object)
        django_file = File(attachment)
        obj.attachment.save(attachment.name, django_file, save=True)
    
    @classmethod
    def load_from_id(cls, pk: int):
        orm_letter = LetterModel.objects.filter(pk=pk).not_sent().first()
        
        if not orm_letter:
            raise ValueError(
                _('Letter with id "{}" is not exists or already sent')
                .format(pk)
            )
        
        return Letter(orm_letter)
    

class Template(BaseEntity):
    model = TemplateModel
    
    @property
    def legend(self) -> str:
        legend = '\n'.join(
            f'{{{{ {key} }}}}: {value}'
            for key, value in
            POSTIE_TEMPLATE_CONTEXTS.get(self.object.event, {}).items()
        )
        
        return legend
    
    def render(self, context: Dict[str, Any]) -> Dict[str, str]:
        subject = DjangoTemplate(self.object.subject).render(Context(context))
        html = DjangoTemplate(self.object.html).render(Context(context))
        plain = DjangoTemplate(self.object.plain).render(Context(context))

        return {
            'subject': subject,
            'html': html,
            'plain': striptags(plain)
        }
    
    def new_letter(
            self, context: Dict[str, Any], recipients: List,
            email_from: str = None, attachments: List = None
    ):
        """
        """
        
        rendered_fields = self.render(context)
        
        if not email_from:
            email_from = settings.DEFAULT_FROM_EMAIL
        
        letter = LetterModel.objects.create(
            subject=rendered_fields['subject'],
            html=rendered_fields['html'],
            plain=rendered_fields['plain'],
            email_from=email_from,
            event=self.object.event,
            recipients=encode_list(recipients)
        )
        letter_entity = Letter(letter)
        
        for attachment in attachments:
            letter_entity.add_attachment(attachment)
        
        return letter_entity
    
    @classmethod
    def from_event(cls, event):
        template = TemplateModel.objects.filter(event=event).first()
        
        if not template:
            raise ValueError(_('No MailTemplate for "{}" event').format(event))
        
        return cls(template)
