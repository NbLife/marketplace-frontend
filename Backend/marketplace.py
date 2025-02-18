from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os
import shutil

app = FastAPI()

# 🔹 Obsługa CORS (żeby frontend działał poprawnie)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Połączenie z MongoDB (Azure CosmosDB)
COSMOS_DB_URL = os.getenv("COSMOS_DB_URL", "mongodb://your_connection_string")
client = MongoClient(COSMOS_DB_URL)
db = client.marketplace

# 🔹 Ścieżka do folderu na obrazki
UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔹 API: Dodaj produkt
@app.post("/add_product")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...)
):
    # Lista kategorii
    categories = ["Electronics", "Clothing", "Home", "Books", "Beauty", "Sports", "Toys", "Others"]
    if category not in categories:
        category = "Others"

    # Zapis obrazka na serwerze
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    with open(image_path, "wb") as img_file:
        shutil.copyfileobj(image.file, img_file)

    # Zapis produktu w bazie danych
    product = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "image_url": image_path
    }
    result = db.products.insert_one(product)
    product["_id"] = str(result.inserted_id)  # Konwersja ObjectId na string
    
    return {"message": "Product added", "product": product}

# 🔹 API: Pobierz wszystkie produkty
@app.get("/products")
def get_products():
    products = list(db.products.find({}, {"_id": 1, "name": 1, "description": 1, "price": 1, "category": 1, "image_url": 1}))
    return [{"id": str(p["_id"]), **p} for p in products]

# 🔹 API: Usuń produkt
@app.delete("/delete_product/{product_id}")
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
