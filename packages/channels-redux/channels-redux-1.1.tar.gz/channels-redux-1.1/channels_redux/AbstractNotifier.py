from django.conf import settings
from django.db import models


class AbstractNotifier(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_api_base_name(cls):
        return '{}:{}'.format(settings.API_APP_NAMESPACE, cls._meta.label_lower)
