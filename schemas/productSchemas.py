from pydantic import BaseModel


class PricePlanSchema(BaseModel):
    plan_name: str
    total_wishes: int
    price: str
    period: str


class ProductBaseSchema(BaseModel):
    product_name: str
    product_module: str | None = None
    module_description: str = ""
    source_check: list[str] = []
    source_text: str | None = None
    source_image: str | None = None
    source_url: str | None = None
    input_box_title: str | None = None
    input_box_description: str = ""
    export_check: list[str] = []
    export_word: str | None = None
    export_pdf: str | None = None
    export_text: str | None = None
    price_plan: list[PricePlanSchema] | None = None

    class Config:
        populate_by_name = True


class ProductUpdateSchema(ProductBaseSchema):
    id: str


class PriceUpdateSchema(BaseModel):
    product_name: str
    product_module: str | None = None
    module_description: str | None = None
    plan_details: list[PricePlanSchema] | None = None
