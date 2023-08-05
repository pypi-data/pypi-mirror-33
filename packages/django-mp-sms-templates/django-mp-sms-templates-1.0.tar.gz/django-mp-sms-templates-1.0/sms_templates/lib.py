
from django.template import Template, Context

from sms_templates.models import SMSTemplate
from sms_templates.exceptions import SMSTemplateDoesNotExist

# TODO: remove turbosms dependency
from turbosms.lib import send_sms


def send_sms_from_template_record(slug, context=None, recipients=None):

    try:
        sms_template = SMSTemplate.objects.get(slug=slug)
    except SMSTemplate.DoesNotExist:
        raise SMSTemplateDoesNotExist('SMS template not found: ' + slug)

    template = Template(sms_template.text)

    if recipients is None:
        recipients = sms_template.get_recipients()

    send_sms(template.render(Context(context)), recipients)
