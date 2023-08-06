
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


from model_search.lib import (
    normalize_query, model_search, tags_search, build_query)


__all__ = ['normalize_query', 'build_query', 'model_search']

__version__ = '2.1'


class ModelSearchConfig(AppConfig):
    name = 'model_search'
    verbose_name = _("Search")


default_app_config = 'model_search.ModelSearchConfig'
