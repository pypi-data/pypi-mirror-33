from django.conf import settings

API_APP_NAMESPACE = getattr(settings, 'API_APP_NAMESPACE', 'api')
