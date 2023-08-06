from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CommentsConfig(AppConfig):
    name = 'comments'
    verbose_name = _("Comments")


default_app_config = 'comments.CommentsConfig'

__version__ = '1.1'
