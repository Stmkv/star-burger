data: dict = {
    "products": [{"product": 2, "quantity": 2}, {"product": 1, "quantity": 2}],
    "firstname": "Степан",
    "lastname": "Макаров",
    "phonenumber": "+79600770542",
    "address": "48/15",
}

product: dict = data["products"][0]
data_product = product.get("product")
print(data_product)
