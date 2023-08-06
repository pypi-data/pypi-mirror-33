
import re
import operator

from django.apps import apps
from django.conf import settings
from django.db.models import Q

try:
    from functools import reduce
except ImportError:
    pass


TERMS = re.compile(r'"([^"]+)"|(\S+)').findall
NORM_SPACE = re.compile(r'\s{2,}').sub


def normalize_query(query_string, terms=TERMS, norm_space=NORM_SPACE):
    """
    Example:
    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    """
    return [
        norm_space(' ', (t[0] or t[1]).strip()) for t in terms(query_string)]


def build_query(query_string, search_fields):

    terms = normalize_query(query_string)

    if not terms:
        return None

    query = reduce(
        operator.__and__,
        (reduce(
            operator.__or__,
            (Q(**{"%s__icontains" % field_name: term})
             for field_name in search_fields)
        ) for term in terms),
    )
    return query


def model_search(query, queryset, fields):

    assert query is not None

    entry_query = build_query(query, fields)

    return queryset.filter(entry_query)


def tags_search(query, queryset, fields):

    tag_fields = ['text_%s' % code for code in dict(settings.LANGUAGES).keys()]

    search_tag_model = apps.get_model('model_search', 'SearchTag')

    tags = model_search(query, search_tag_model.objects.all(), tag_fields)

    return queryset.filter(Q(tags__in=tags) | build_query(query, fields))
