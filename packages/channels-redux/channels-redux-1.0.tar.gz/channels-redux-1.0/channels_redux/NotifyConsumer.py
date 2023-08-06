import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.urls import NoReverseMatch
from rest_framework.reverse import reverse

from channels_redux.NotifierMixin import NotifierMixin

ats = async_to_sync


class NotifyConsumer(AsyncWebsocketConsumer):
    @property
    def user(self):
        return self.scope["user"]

    async def connect(self):
        if self.user.is_anonymous:
            await self.close()

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        operation = {
            "subscribe.new": self.subscribe_new,
            "subscribe.existing": self.subscribe_existing,
        }.get(json_data["type"], None)

        if operation is None:
            raise NotImplementedError("Operation {} is not supported. Received data {}".format(operation, json_data))
        await operation(json_data)

    async def subscribe_new(self, message: dict):
        await self.subscribe_to_group(message['model'])

    async def subscribe_existing(self, message: dict):
        model = message['model']
        ids = message['ids']
        for pk in ids:
            await self.subscribe_to_group(self.group_name(model, pk))

    async def subscribe_to_group(self, group_name):
        await self.channel_layer.group_add(group_name, self.channel_name)

    async def notify(self, event):
        await self.send(text_data=json.dumps({
            "model": event['model'],
            "pk": event['pk'],
            "type": event['subtype'],
            "url": event['url']
        }))

    @staticmethod
    def group_name(model, pk=None):
        return '{}.{}'.format(model, pk) if pk else model

    @staticmethod
    def object_updated(instance: NotifierMixin):
        channel_layer = get_channel_layer()
        message = NotifyConsumer.message_for_type("updated", instance)
        ats(channel_layer.group_send)(NotifyConsumer.group_name(message["model"], instance.pk), message)

    @staticmethod
    def object_created(instance: NotifierMixin):
        channel_layer = get_channel_layer()
        message = NotifyConsumer.message_for_type("created", instance)
        ats(channel_layer.group_send)(NotifyConsumer.group_name(message["model"]), message)

    @staticmethod
    def object_deleted(instance: NotifierMixin):
        channel_layer = get_channel_layer()
        message = NotifyConsumer.message_for_type("deleted", instance)
        ats(channel_layer.group_send)(NotifyConsumer.group_name(message["model"], instance.pk), message)

    @staticmethod
    def message_for_type(message_type, instance: NotifierMixin):
        try:
            return {
                "type": "notify",
                "subtype": message_type,
                "model": instance._meta.label_lower,
                "pk": instance.pk,
                "url": reverse('{}-detail'.format(instance.get_api_base_name()), args=(instance.pk,)),
            }
        except NoReverseMatch:
            print('API url does not exist for {}'.format(instance.get_api_base_name()))
