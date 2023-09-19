from pydantic import BaseModel


class PromptBaseSchema(BaseModel):
    product: str
    plan: str
    module: str
    prompt_name: str
    order: int
    prompt: str


class RunPromptSchema(BaseModel):
    product_name: str
    product_module: str
    code: str
