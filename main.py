from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import openai

from routers import products, prompts, auth, user, genie
from config import settings
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [settings.CLIENT_ORIGIN, "https://main.d1l17mtvn7i9t6.amplifyapp.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["Prompts"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(genie.router, prefix="/api/genie", tags=["Genie"])


@app.get("/")
async def health_checker():
    return {"status": "success"}
