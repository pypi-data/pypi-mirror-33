
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CommentAnswer(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True,
        null=True, related_name="comment_answers", on_delete=models.SET_NULL)

    text = models.TextField(_('Text'), max_length=10000)

    created = models.DateTimeField(_('Created'), auto_now=True, db_index=True)

    @property
    def name(self):
        if self.user:
            return self.user.get_full_name()
        return _('Administrator')


class Comment(models.Model):

    answer = models.OneToOneField(
        CommentAnswer, null=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(_('Is active'), default=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('User'), blank=True,
        null=True, related_name="comments", on_delete=models.SET_NULL)

    name = models.CharField('Name', blank=True, max_length=128)

    email = models.EmailField(_('Email'), blank=True, null=True)

    text = models.TextField(_('Text'), max_length=10000)

    created = models.DateTimeField(_('Created'), auto_now=True, db_index=True)

    ip_address = models.GenericIPAddressField(
        _('IP address'), unpack_ipv4=True, blank=True, null=True)

    def __str__(self):
        return ugettext('Comment')

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
