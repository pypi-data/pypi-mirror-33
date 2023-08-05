from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, NoReverseMatch

from wagtail.admin.edit_handlers import PageChooserPanel, FieldPanel
from wagtail.snippets.models import register_snippet

import logging

logger = logging.getLogger(__name__)


def validate_django_reverse(view_name):
    try:
        reverse(view_name)
    except NoReverseMatch:
        raise ValidationError(_('Invalid django view name'))


@register_snippet
class Link(models.Model):
    """
    A generic link that points somewhere else using various methods
    """
    link_external = models.URLField("External link", blank=True)
    link_relative = models.CharField(
        "Relative link",
        max_length=200,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^(?!www\.|(?:http|ftp)s?://|[A-Za-z]:\\|//).*',
                message='Not valid relative url',
            ),
        ]
    )
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE,
    )
    django_view_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of django view for reverse lookup",
        validators=[
            validate_django_reverse,
        ],
    )

    panels = [
        FieldPanel('link_external'),
        FieldPanel('link_relative'),
        PageChooserPanel('link_page'),
        FieldPanel('django_view_name'),
    ]

    def __str__(self):
        if self.link_external:
            return self.link_external
        elif self.link_relative:
            return self.link_relative
        elif self.link_page:
            return str(self.link_page)
        return self.django_view_name

    @property
    def url(self):
        """ Get url for use in template """
        if self.link_external:
            return self.link_external
        elif self.link_relative:
            return self.link_relative
        elif self.link_page:
            url = self.link_page.url
            if url is None:
                return ''
            return url
        else:
            try:
                return reverse(self.django_view_name)
            except NoReverseMatch:
                logger.warning(
                    'Unable to reverse django url for link id {}'.format(
                        self.id)
                )
                return ''

    def clean(self):
        # Don't allow multiple to be used
        number_used = bool(self.link_external) + bool(self.link_relative) \
            + bool(self.link_page) + bool(self.django_view_name)
        if number_used > 1:
            raise ValidationError(_('Use only one link type'))
        if number_used == 0:
            raise ValidationError(_('Must use exactly one link type'))
