import requests
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.serializers import ModelSerializer

from geo.models import Place
from geo.views import fetch_coordinates

from .models import Order, OrderItem


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ["id", "firstname", "lastname", "phonenumber", "address", "products"]

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data["firstname"],
            lastname=validated_data["lastname"],
            phonenumber=validated_data["phonenumber"],
            address=validated_data["address"],
        )

        order_item_field = validated_data["products"]
        order_items = [OrderItem(order=order, **fields) for fields in order_item_field]
        OrderItem.objects.bulk_create(order_items)

        place, created = Place.objects.update_or_create(
            address=order.address, defaults={"create_date": timezone.now()}
        )

        try:
            if created:
                coordinates = fetch_coordinates(settings.YANDEX_API_KEY, order.address)
                place.longitude, place.latitude = coordinates
                place.save()
        except requests.exceptions.HTTPError:
            place.longitude, place.latitude = 0, 0
            place.save()
        return order


@receiver(post_save, sender=Order)
def update_place_on_order_change(sender, instance, **kwargs):
    place, created = Place.objects.update_or_create(
        address=instance.address, defaults={"create_date": timezone.now()}
    )
    try:
        if created:
            coordinates = fetch_coordinates(settings.YANDEX_API_KEY, instance.address)
            place.longitude, place.latitude = coordinates
            place.save()
    except requests.exceptions.HTTPError:
        print("Не удалось распознать адрес")
