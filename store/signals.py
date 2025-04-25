from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, Cart




@receiver(post_save, sender=Customer)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(customer=instance)