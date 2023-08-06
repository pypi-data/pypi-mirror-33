
from importlib import import_module

from django.apps import apps
from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, render, redirect

try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy

from sms_templates.models import SMSTemplate
from sms_templates.forms import SendSMSForm

# TODO: remove turbosms dependency
from turbosms.lib import send_sms


def _get_sms_template_admin_base_class():

    if apps.is_installed('modeltranslation'):
        return import_module('modeltranslation.admin').TranslationAdmin

    return admin.ModelAdmin


class SMSTemplateAdmin(_get_sms_template_admin_base_class()):

    list_display = ['name', 'slug', 'send_sms_link']
    search_fields = ['name', 'slug', 'recipients', 'text']

    def get_readonly_fields(self, request, obj=None):
        return ['placeholders'] if obj else []

    def send_sms_link(self, item):
        html = """
            <a class="btn btn-primary btn-block pull-right" href="{}">
                <i class="fa fa-upload"></i> {}
            </a>
        """
        return html.format(
            reverse_lazy('admin:send-sms', args=[item.id]), _('Send'))

    send_sms_link.short_description = _('Actions')
    send_sms_link.allow_tags = True

    def get_urls(self):

        return [
            url(r'^(.+)/send/$', self.send_sms_template, name='send-sms'),
        ] + super(SMSTemplateAdmin, self).get_urls()

    def send_sms_template(self, request, object_id):

        template = get_object_or_404(SMSTemplate, pk=object_id)

        form = SendSMSForm(request.POST or None, instance=template)

        if request.method == 'POST' and form.is_valid():
            data = form.cleaned_data
            send_sms(data['text'], data['recipients'])
            messages.success(request, _('SMS was sent'))
            return redirect('admin:smstemplates_smstemplate_changelist')

        return render(request, 'sms_templates/send_sms.html', {'form': form})


admin.site.register(SMSTemplate, SMSTemplateAdmin)
