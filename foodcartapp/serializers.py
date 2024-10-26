import io
from ast import Delete
from dataclasses import field

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ListField, ModelSerializer

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

        return order
