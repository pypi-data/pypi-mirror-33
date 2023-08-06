from channels.routing import URLRouter
from django.conf.urls import url

from channels_redux import NotifyConsumer


class NotifyRouter(URLRouter):
    def __init__(self, path=r'^ws/notify/$', name='ws-notify'):
        super().__init__([url(path, NotifyConsumer, name=name)])
