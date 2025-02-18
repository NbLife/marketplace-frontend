from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()
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
    if category not in ["Electronics", "Clothing", "Home", "Books", "Beauty", "Sports", "Toys", "Others"]:
        category = "Others"
    image_path = f"images/{image.filename}"
    with open(image_path, "wb") as img_file:
        img_file.write(image.file.read())
    product = {"name": name, "description": description, "price": price, "category": category, "image_url": image_path}
    db.products.insert_one(product)
    return {"message": "Product added"}

@app.get("/products")
def get_products():
    products = list(db.products.find({}, {"_id": 1, "name": 1, "description": 1, "price": 1, "category": 1, "image_url": 1}))
    return [{"id": str(p["_id"]), **p} for p in products]

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: str):
    db.products.delete_one({"_id": ObjectId(product_id)})
    return {"message": "Product deleted"}
