from django.db.models import Manager, Avg
from django.db.models.query import QuerySet

from django.contrib.contenttypes.models import ContentType


class ActiveMixin(object):
    """
    An extended manager to return active objects.
    """
    def active(self):
        return self.filter(active=True)

    def average(self, instance=None):
        queryset = self
        if instance:
            queryset = queryset.filter(object_id=instance.id, content_type=ContentType.objects.get_for_model(instance))
        avg_dict = queryset.aggregate(average=Avg('score'))
        return avg_dict.get('average', 0)


class ActiveQuerySet(ActiveMixin, QuerySet):
    pass


class ActiveManager(ActiveMixin, Manager):
    def get_queryset(self):
        return ActiveQuerySet(self.model, using=self._db)
