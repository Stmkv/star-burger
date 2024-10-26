from django.http import Http404, JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.test import APITestCase

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse(
        [
            {
                "title": "Burger",
                "src": static("burger.jpg"),
                "text": "Tasty Burger at your door step",
            },
            {
                "title": "Spices",
                "src": static("food.jpg"),
                "text": "All Cuisines",
            },
            {
                "title": "New York",
                "src": static("tasty.jpg"),
                "text": "Food is incomplete without a tasty dessert",
            },
        ],
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


def product_list_api(request):
    products = Product.objects.select_related("category").available()

    dumped_products = []
    for product in products:
        dumped_product = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "special_status": product.special_status,
            "description": product.description,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
            }
            if product.category
            else None,
            "image": product.image.url,
            "restaurant": {
                "id": product.id,
                "name": product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(
        dumped_products,
        safe=False,
        json_dumps_params={
            "ensure_ascii": False,
            "indent": 4,
        },
    )


@api_view(["POST"])
def register_order(request):
    data = request.data
    if (
        "products" not in data
        or not isinstance(data["products"], list)
        or not data["products"]
    ):
        return Response(
            {"error": "products key not presented or not lsit"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order = Order.objects.create(
        first_name=data["firstname"],
        last_name=data["lastname"],
        phone_number=data["phonenumber"],
        address=data["address"],
    )

    for user_order in data["products"]:
        product_id = user_order.get("product")
        product_quantity = user_order.get("quantity")

        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order, product=product, quantity=product_quantity
        )
    return Response(data)
