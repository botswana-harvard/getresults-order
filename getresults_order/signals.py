from django.db.models.signals import post_save
from django.dispatch import receiver

from .order_identifier import OrderIdentifier


@receiver(post_save, weak=False, dispatch_uid='order_on_post_save')
def order_on_post_save(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw:
        instance.order_identifier = OrderIdentifier().identifier
        instance.save()
