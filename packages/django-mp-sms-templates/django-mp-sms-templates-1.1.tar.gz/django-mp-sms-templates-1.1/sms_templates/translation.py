
from modeltranslation.translator import translator, TranslationOptions

from sms_templates.models import SMSTemplate


class SMSTemplateTranslationOptions(TranslationOptions):
    fields = ['text']


translator.register(SMSTemplate, SMSTemplateTranslationOptions)
