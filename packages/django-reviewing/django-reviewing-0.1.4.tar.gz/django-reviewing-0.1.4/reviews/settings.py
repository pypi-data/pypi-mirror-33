from django.conf import settings
from django.utils.translation import ugettext_lazy as _


DEFAULT_SCORE_CHOICES = (
    (1, _(u"*")),
    (2, _(u"**")),
    (3, _(u"***")),
    (4, _(u"****")),
    (5, _(u"*****")),
)


SCORE_CHOICES = getattr(settings, 'SCORE_CHOICES', DEFAULT_SCORE_CHOICES)
