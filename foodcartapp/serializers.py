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
