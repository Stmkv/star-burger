from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list(
            "product"
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField("в продаже", default=True, db_index=True)

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [["restaurant", "product"]]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_total_price(self):
        return self.annotate(
            total_price=models.Sum("items__product__price")
            * models.F("items__quantity")
        )


class Order(models.Model):
    UNPROCESSING = "new"
    PROCESSING = "prc"
    IN_DELEVERY = "del"
    COMPLETED = "com"

    ORDER_STATUS_CHOICES = [
        (UNPROCESSING, "Необработанный"),
        (PROCESSING, "Готовится"),
        (IN_DELEVERY, "В доставке"),
        (COMPLETED, "Завершен"),
    ]
    ORDER_PAYMENT_METHOD = [
        ("card", "По карте"),
        ("cash", "Наличные"),
    ]

    firstname = models.CharField("Имя", max_length=20, null=False)
    lastname = models.CharField("Фамилия", max_length=20, null=False)
    phonenumber = PhoneNumberField("Телефон", null=False, db_index=True)
    address = models.CharField(verbose_name="Адресс", max_length=200, null=False)
    status = models.CharField(
        verbose_name="Статус заказа",
        choices=ORDER_STATUS_CHOICES,
        default=UNPROCESSING,
        max_length=3,
        db_index=True,
    )
    payment_method = models.CharField(
        verbose_name="Способ оплаты",
        choices=ORDER_PAYMENT_METHOD,
        default="По карте",
        db_index=True,
    )
    comments = models.TextField(verbose_name="Комментарии", blank=True, default="")
    register_at = models.DateTimeField(
        "Дата создания", auto_now_add=True, db_index=True
    )
    called_at = models.DateTimeField(
        "Дата звонка ", null=True, blank=True, db_index=True
    )
    delivered_at = models.DateTimeField(
        "Дата доставки", null=True, blank=True, db_index=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.address}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE, verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        related_name="ordered_items",
        verbose_name="продукт",
    )
    quantity = models.PositiveIntegerField(
        "количество", validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        "Цена",
        validators=[MinValueValidator(1)],
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Заказанный товар"
        verbose_name_plural = "Заказанные товары"

    def __str__(self):
        return f"{self.product.name} {self.order.firstname} {self.order.lastname} {self.order.address}"
