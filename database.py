from pymongo import MongoClient, ASCENDING
from config import settings

client = MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect MongoDB Server.")

db = client[settings.MONGO_INITDB_DATABASE]

Products = db.products
Prompts = db.prompts
Users = db.users
