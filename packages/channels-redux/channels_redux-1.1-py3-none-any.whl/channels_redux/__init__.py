from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from channels_redux.NotifyConsumer import NotifyConsumer
from channels_redux.AbstractNotifier import AbstractNotifier
from channels_redux.NotifyRouter import NotifyRouter

__all__ = [
    'NotifyConsumer',
    'AbstractNotifier',
    'NotifyRouter'
]


@receiver(post_save)
def object_saved(sender, instance: AbstractNotifier, created, **kwargs):
    if not issubclass(sender, AbstractNotifier):
        return
    if created:
        NotifyConsumer.object_created(instance)
    else:
        NotifyConsumer.object_updated(instance)


@receiver(post_delete)
def object_deleted(sender, instance: AbstractNotifier, **kwargs):
    if not issubclass(sender, AbstractNotifier):
        return
    NotifyConsumer.object_deleted(instance)
