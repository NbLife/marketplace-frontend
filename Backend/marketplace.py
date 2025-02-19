from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Zezwól na żądania CORS tylko z Twojej strony frontendowej
CORS(app, origins=["https://red-tree-02e732c0f.4.azurestaticapps.net"])

# Przykładowa baza produktów
products = [
    {"id": 1, "name": "Laptop", "price": 3000, "image": "laptop.jpg"},
    {"id": 2, "name": "Telefon", "price": 2000, "image": "phone.jpg"}
]

@app.route('/')
def home():
    return "Marketplace API is running!"

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products), 200

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data or "name" not in data or "price" not in data:
        return jsonify({"error": "Invalid request. 'name' and 'price' are required."}), 400
    
    new_product = {
        "id": len(products) + 1,
        "name": data["name"],
        "price": data["price"],
        "image": data.get("image", "default.jpg")
    }
    products.append(new_product)
    return jsonify(new_product), 201

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products
    products = [p for p in products if p["id"] != product_id]
    return jsonify({"message": "Product deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)