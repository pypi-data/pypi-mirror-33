from django.conf import settings


class NotifierMixin(object):
    @classmethod
    def get_api_base_name(cls):
        return '{}:{}'.format(settings.API_APP_NAMESPACE, cls._meta.label_lower)
