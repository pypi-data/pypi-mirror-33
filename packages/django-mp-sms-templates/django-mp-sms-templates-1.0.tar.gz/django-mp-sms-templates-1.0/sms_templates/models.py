
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SMSTemplate(models.Model):

    name = models.CharField(_('Name'), max_length=255)

    slug = models.CharField(
        _('Slug'), unique=True, db_index=True, max_length=255)

    recipients = models.TextField(
        _('Recipients'), max_length=1000, blank=True, null=True,
        help_text=_('One phone number for one line'))

    text = models.TextField(_('Message'), max_length=1024)

    placeholders = models.TextField(
        _('Placeholders'), max_length=4096, blank=True, null=True)

    def get_recipients(self):
        return self.recipients.split('\n') if self.recipients else None

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = _('SMS Template')
        verbose_name_plural = _('SMS Templates')
