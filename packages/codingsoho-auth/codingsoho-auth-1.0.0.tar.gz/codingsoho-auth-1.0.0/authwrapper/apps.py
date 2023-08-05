from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class AuthConfig(AppConfig):
    name = 'authwrapper'
    verbose_name = _("authwrapper")
