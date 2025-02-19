from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()


origins = [
    "https://red-tree-02e732c0f.4.azurestaticapps.net",  # Twój frontend na Azure
    "http://localhost:8000"  # Twój backend lokalnie
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os
from pymongo import MongoClient

MONGO_URL = os.getenv("COSMOS_DB_URL")

print(f"🔗 Próba połączenia z MongoDB: {MONGO_URL}")

try:
    client = MongoClient(MONGO_URL)
    db = client.marketplace
    db.command("ping")
    print("✅ Połączenie z Cosmos DB działa!")
except Exception as e:
    print(f"❌ Błąd połączenia z Cosmos DB: {e}")


# Pobieranie connection string z GitHub Secrets
MONGO_URL = os.getenv("COSMOS_DB_URL")
if not MONGO_URL:
    raise Exception("❌ Błąd: Zmienna COSMOS_DB_URL nie jest ustawiona!")

# Sprawdzenie połączenia do Cosmos DB
try:
    print(f"🔗 Connecting to MongoDB: {MONGO_URL}")
    client = MongoClient(MONGO_URL)
    db = client.marketplace
    db.command("ping")  # Sprawdzenie, czy baza działa
    print("✅ Połączenie z Cosmos DB nawiązane!")
except Exception as e:
    print(f"❌ Błąd połączenia z Cosmos DB: {e}")
    raise Exception("Nie można połączyć się z Cosmos DB!")

@app.post("/add_product")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...)
):
    categories = ["Electronics", "Clothing", "Home", "Books", "Beauty", "Sports", "Toys", "Others"]
    if category not in categories:
        category = "Others"

    # Zapis obrazu lokalnie (lub do chmury, np. Azure Blob Storage)
    image_path = f"images/{image.filename}"
    os.makedirs("images", exist_ok=True)
    with open(image_path, "wb") as img_file:
        img_file.write(image.file.read())

    product = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "image_url": image_path
    }
    result = db.products.insert_one(product)
    return {"message": "Product added", "id": str(result.inserted_id)}

@app.get("/products")
def get_products():
    products = list(db.products.find({}, {"_id": 1, "name": 1, "description": 1, "price": 1, "category": 1, "image_url": 1}))
    return [{"id": str(p["_id"]), **p} for p in products]

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="❌ Product not found")
    return {"message": "✅ Product deleted"}
