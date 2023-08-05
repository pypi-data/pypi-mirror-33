
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SMSTemplatesConfig(AppConfig):
    name = 'sms_templates'
    verbose_name = _("SMS templates")


default_app_config = 'sms_templates.SMSTemplatesConfig'

__version__ = '1.0'
