
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SearchTagGroup(models.Model):

    name = models.CharField(_('Group name'), max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Search tag group')
        verbose_name_plural = _('Search tag groups')


class SearchTag(models.Model):

    group = models.ForeignKey(
        SearchTagGroup, verbose_name=_('Group'), related_name='tags')

    text = models.CharField(_('Text'), max_length=255, unique=True)

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = _('Search tag')
        verbose_name_plural = _('Search tags')


class SearchQuery(models.Model):

    url = models.URLField(_('URL'), max_length=255)

    text = models.CharField(_('Text'), max_length=255, unique=True)

    result_count = models.IntegerField(_('Result count'))

    def __unicode__(self):
        return self.text

    @classmethod
    def add(cls, url, text, result_count):
        return cls.objects.get_or_create(
            url=url, text=text, result_count=result_count)

    class Meta:
        verbose_name = _('Search query')
        verbose_name_plural = _('Search queries')
