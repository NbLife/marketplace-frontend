from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()

# ✅ Poprawiona konfiguracja CORS
origins = [
    "http://127.0.0.1:5500",  # Lokalny serwer (np. Live Server w VS Code)
    "http://localhost:8000",  # Backend w trybie lokalnym
    "https://red-tree-02e732c0f.4.azurestaticapps.net"  # Adres Twojej aplikacji na Azure
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Możesz tu dodać dokładne adresy np. "https://twoja-strona.azurestaticapps.net"
    allow_credentials=True,
    allow_methods=["*"],  # Pozwala na wszystkie metody (GET, POST, DELETE, itd.)
    allow_headers=["*"],  # Pozwala na wszystkie nagłówki
)


client = MongoClient(os.getenv("COSMOS_DB_URL"))  # Pobiera klucz z env
db = client.marketplace

# ✅ Obsługa dodawania produktu
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
    db.products.insert_one(product)
    return {"message": "Product added", "product": product}

# ✅ Pobieranie produktów
@app.get("/products")
def get_products():
    products = list(db.products.find({}, {"_id": 1, "name": 1, "description": 1, "price": 1, "category": 1, "image_url": 1}))
    return [{"id": str(p["_id"]), **p} for p in products]

# ✅ Usuwanie produktu
@app.delete("/delete_product/{product_id}")
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
