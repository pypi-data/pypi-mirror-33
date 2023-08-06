from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from codemirror2.widgets import AdminCodeMirrorEditor
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from .models import Attachment, Log
from .entities import Template, Letter


__all__ = (
    'TemplateAdmin',
    'LetterAdmin'
)


class TemplateForm(TranslatableModelForm):
    html = forms.CharField(
        widget=AdminCodeMirrorEditor(
            modes=['css', 'xml', 'javascript', 'htmlmixed']
        )
    )
    context = forms.CharField(
        label=_('Context'), widget=forms.Textarea(), disabled=True,
        required=False
    )

    class Meta:
        model = Template.model
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields['context'].initial = Template(self.instance).legend


class AddTemplateForm(TranslatableModelForm):
    class Meta:
        model = Template.model
        fields = ['name', 'event']


@admin.register(Template.model)
class TemplateAdmin(TranslatableAdmin):
    """
    Admin interface for mail.
    """
    list_display = ['event', 'subject']
    form = TemplateForm
    add_form = AddTemplateForm
    fieldsets = (
        (None, {
            'fields': [
                'name', 'event',
            ]
        }),
        (_('Template'), {
            'fields': [
                'subject', 'html', 'context', 'plain'
            ]
        })
    )
    add_fieldsets = (
        (None, {
            'fields': [
                'name', 'event'
            ]
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}

        if obj is None:
            defaults['form'] = self.add_form

        defaults.update(kwargs)

        return super().get_form(request, obj, **defaults)


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0


class LogInline(admin.StackedInline):
    model = Log
    extra = 0

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False


def send_letters(modeladmin, request, queryset) -> None:
    """
    Sends selected letters.
    """

    for letter in queryset:
        letter.entity.send()


send_letters.short_description = "Send letters"


@admin.register(Letter.model)
class LetterAdmin(admin.ModelAdmin):
    """
    Admin interface for mail.
    """

    list_display = ['subject', 'status', 'event', 'created']
    list_filter = ['status', 'event']
    search_fields = ['subject', 'recipients']

    inlines = [AttachmentInline, LogInline]
    actions = [send_letters]
