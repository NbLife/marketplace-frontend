import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# Obsługa CORS - umożliwia komunikację między frontendem a backendem
origins = [
    "http://localhost:5500",  # Live Server w VS Code
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "*"  # Dla testów, można usunąć po wdrożeniu
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pobieranie adresu MongoDB z GitHub Actions lub zmiennych środowiskowych
MONGO_URL = os.getenv("COSMOS_DB_URL", "mongodb://localhost:27017")  # Domyślna lokalna baza danych dla testów
client = MongoClient(MONGO_URL)
db = client.marketplace

# Katalog do przechowywania obrazów
UPLOAD_FOLDER = "static/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    
    image_path = f"{UPLOAD_FOLDER}/{image.filename}"
    with open(image_path, "wb") as img_file:
        img_file.write(image.file.read())
    
    product = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "image_url": f"/{image_path}"  # Ścieżka względna
    }
    inserted = db.products.insert_one(product)
    return {"message": "Product added", "id": str(inserted.inserted_id), "product": product}

@app.get("/products")
def get_products():
    products = list(db.products.find({}, {"_id": 1, "name": 1, "description": 1, "price": 1, "category": 1, "image_url": 1}))
    return [{"id": str(p["_id"]), **p} for p in products]

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: str):
    result = db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
