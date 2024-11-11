from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from geo.models import Place
from geo.views import fetch_coordinates
from star_burger import settings


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Укажите имя пользователя"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False) for restaurant in restaurants
        ]

        products_with_restaurant_availability.append((product, ordered_availability))

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = (
        Order.objects.get_total_price().prefetch_related("items").order_by("status")
    )
    menu_item = RestaurantMenuItem.objects.filter(availability=True)
    restaurants = Restaurant.objects.all()
    places = Place.objects.all()

    for order in orders:
        for item in order.items.all():
            restorants = menu_item.filter(product=item.product).values_list(
                "restaurant__name", flat=True
            )
        order.restaurants = restorants
        if order.restaurant:
            order.status = "prc"

        buyer_place = places.get(address=order.address)
        buyer_coordinates_lon_lat = (buyer_place.longitude, buyer_place.latitude)

        restorants_distances = []
        for restaurant in order.restaurants:
            restaurant = restaurants.get(name=restaurant)
            restaurant_address = restaurant.address
            restorant_coordinates_lon_lat_test = fetch_coordinates(
                settings.YANDEX_API_KEY, restaurant_address
            )
            restaurant_coordinates_lon_lat = (
                restorant_coordinates_lon_lat_test[0],
                restorant_coordinates_lon_lat_test[1],
            )
            if restaurant_coordinates_lon_lat and buyer_coordinates_lon_lat:
                restorant_distance = round(
                    distance.distance(
                        buyer_coordinates_lon_lat,
                        restaurant_coordinates_lon_lat,
                    ).km,
                    2,
                )

            restorants_distances.append((restaurant, restorant_distance))
        order.restorants_distance = sorted(
            restorants_distances, key=lambda x: x[1], reverse=True
        )
    return render(
        request,
        template_name="order_items.html",
        context={"orders": orders},
    )
