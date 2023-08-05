from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ImgurConfig(AppConfig):
    name = 'my_imgur'
    verbose_name = _('My Imgur')
