from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()

# Dodanie obsługi CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb://your_connection_string")
db = client.marketplace

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
