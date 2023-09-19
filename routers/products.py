from fastapi import APIRouter, Body, HTTPException, status
from bson.objectid import ObjectId

from database import Products
from schemas import productSchemas
from serializers.productSerializers import productsEntity

router = APIRouter()


@router.get("/")
async def get_product(product_name: str, product_module: str):
    product = Products.find_one(
        {"product_name": product_name, "product_module": product_module}
    )
    if product:
        del product["_id"]
    return {"status": "success", "data": product}


@router.get("/search")
async def search_product(search_key: str):
    query = {
        "$or": [
            {"product_name": {"$regex": search_key}},
            {"product_module": {"$regex": search_key}},
        ]
    }
    results = Products.find(query, projection={"_id", "product_name", "product_module"})
    results = productsEntity(results)
    return {"status": "success", "data": results}


@router.post("/")
async def add_product(product: productSchemas.ProductBaseSchema):
    existing_one = Products.find_one(
        {"product_name": product.product_name, "product_module": product.product_module}
    )
    if existing_one:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product name and product module have conflicts.",
        )
    else:
        Products.insert_one(product.dict())
    return {"status": "success"}


@router.patch("/")
async def update_product(product: productSchemas.ProductUpdateSchema):
    data = product.dict()
    del data["id"]
    Products.update_one(
        {"_id": ObjectId(product.id)},
        {"$set": data},
    )
    return {"status": "success"}


@router.patch("/update_price")
async def update_price(product: productSchemas.PriceUpdateSchema):
    existing_one = Products.find_one(
        {"product_name": product.product_name, "product_module": product.product_module}
    )
    print(product)
    if not existing_one:
        Products.insert_one(product.dict())
    else:
        Products.update_one(
            {
                "product_name": product.product_name,
                "product_module": product.product_module,
            },
            {"$set": product.dict()},
        )


@router.get("/names")
async def get_product_names():
    product_names = Products.distinct("product_name")
    return {"status": "success", "data": list(product_names)}


@router.get("/modules")
async def get_moudles_from_product_name(product_name: str):
    products = Products.find(
        {"product_name": product_name}, projection={"product_module": 1, "_id": 0}
    )
    return {"status": "success", "data": list(products)}


@router.get("/prices")
async def get_prices(product_name: str, product_module: str):
    products = Products.find_one(
        {"product_name": product_name, "product_module": product_module},
        projection={"plan_details": 1, "_id": 0},
    )
    print(dict(products))
    return {"status": "success", "data": dict(products)}
