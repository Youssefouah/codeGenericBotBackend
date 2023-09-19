def productEntity(product) -> dict:
    _id = str(product["_id"])
    del product["_id"]
    product["_id"] = _id
    return product


def productsEntity(products):
    return [productEntity(product) for product in products]
