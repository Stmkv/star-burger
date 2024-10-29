from dataclasses import field
from gettext import install

from django.contrib import admin
from django.db import transaction
from django.forms import BaseModelFormSet, ModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (
    Order,
    OrderItem,
    Product,
    ProductCategory,
    Restaurant,
    RestaurantMenuItem,
)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "address",
        "contact_phone",
    ]
    list_display = [
        "name",
        "address",
        "contact_phone",
    ]
    inlines = [RestaurantMenuItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "get_image_list_preview",
        "name",
        "category",
        "price",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = [
        "category",
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        "name",
        "category__name",
    ]

    inlines = [RestaurantMenuItemInline]
    fieldsets = (
        (
            "Общее",
            {
                "fields": [
                    "name",
                    "category",
                    "image",
                    "get_image_preview",
                    "price",
                ]
            },
        ),
        (
            "Подробно",
            {
                "fields": [
                    "special_status",
                    "description",
                ],
                "classes": ["wide"],
            },
        ),
    )

    readonly_fields = [
        "get_image_preview",
    ]

    class Media:
        css = {"all": (static("admin/foodcartapp.css"))}

    def get_image_preview(self, obj):
        if not obj.image:
            return "выберите картинку"
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url
        )

    get_image_preview.short_description = "превью"

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return "нет картинки"
        edit_url = reverse("admin:foodcartapp_product_change", args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url,
            src=obj.image.url,
        )

    get_image_list_preview.short_description = "превью"


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemLine(admin.TabularInline):
    model = OrderItem
    fields = ["product", "quantity", "price"]

    short_description = "Товар"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemLine]

    def save_formset(self, request, form, formset, change):
        order_items = formset.save(commit=False)
        for item in order_items:
            if item.price == 0.00:
                product = Product.objects.get(id=item.product.id)
                item.price = product.price
                item.save()
            else:
                item.save()

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET and url_has_allowed_host_and_scheme(
            request.GET["next"], request.get_host()
        ):
            return HttpResponseRedirect(reverse("restaurateur:view_orders"))
        else:
            return res
