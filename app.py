from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "price": 350.0,
        "quantity": 10,
        "barcode": "3017620422003",
        "brand": "Silk"
    },
    {
        "id": 2,
        "name": "Whole Wheat Bread",
        "price": 120.0,
        "quantity": 20,
        "barcode": "",
        "brand": "Local Bakery"
    }
]


def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def next_id():
    return max([item["id"] for item in inventory], default=0) + 1


def fetch_product(url, params=None):
    response = requests.get(
        url,
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Inventory Management API"})


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory)


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item)


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON is required"}), 400

    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name is required"}), 400

    if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
        return jsonify({"error": "Invalid price"}), 400

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Invalid quantity"}), 400

    barcode = data.get("barcode", "")
    brand = data.get("brand", "")

    if not isinstance(barcode, str) or not isinstance(brand, str):
        return jsonify({"error": "Barcode and brand must be text"}), 400

    item = {
        "id": next_id(),
        "name": name.strip(),
        "price": price,
        "quantity": quantity,
        "barcode": barcode.strip(),
        "brand": brand.strip()
    }

    inventory.append(item)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    data = request.get_json(silent=True)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Valid update data is required"}), 400

    allowed = ["name", "price", "quantity", "barcode", "brand"]

    if any(field not in allowed for field in data):
        return jsonify({"error": "Invalid field"}), 400

    if "name" in data and (
        not isinstance(data["name"], str) or not data["name"].strip()
    ):
        return jsonify({"error": "Invalid name"}), 400

    if "price" in data and (
        isinstance(data["price"], bool)
        or not isinstance(data["price"], (int, float))
        or data["price"] < 0
    ):
        return jsonify({"error": "Invalid price"}), 400

    if "quantity" in data and (
        isinstance(data["quantity"], bool)
        or not isinstance(data["quantity"], int)
        or data["quantity"] < 0
    ):
        return jsonify({"error": "Invalid quantity"}), 400

    for field in ["barcode", "brand"]:
        if field in data and not isinstance(data[field], str):
            return jsonify({"error": f"Invalid {field}"}), 400

    for field, value in data.items():
        item[field] = value.strip() if isinstance(value, str) else value

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return "", 204


@app.route("/external/barcode/<barcode>", methods=["GET"])
def find_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    try:
        result = fetch_product(url)
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Could not fetch product"}), 502

    if result.get("status") != 1:
        return jsonify({"error": "Product not found"}), 404

    product = result.get("product", {})

    return jsonify({
        "barcode": barcode,
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
        "quantity": product.get("quantity", "")
    })


@app.route("/external/search", methods=["GET"])
def search_product():
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({"error": "Product name is required"}), 400

    try:
        result = fetch_product(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={
                "search_terms": name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 5
            }
        )
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Could not search products"}), 502

    products = []

    for product in result.get("products", []):
        products.append({
            "name": product.get("product_name", ""),
            "brand": product.get("brands", ""),
            "barcode": product.get("code", ""),
            "ingredients": product.get("ingredients_text", "")
        })

    return jsonify(products)


@app.route("/external/import/<barcode>", methods=["POST"])
def import_product(barcode):
    try:
        result = fetch_product(
            f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        )
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Could not fetch product"}), 502

    if result.get("status") != 1:
        return jsonify({"error": "Product not found"}), 404

    product = result.get("product", {})
    name = product.get("product_name", "").strip()

    if not name:
        return jsonify({"error": "Product name is missing"}), 422

    for item in inventory:
        if item["barcode"] == barcode:
            return jsonify({
                "message": "Product already exists",
                "item": item
            }), 200

    item = {
        "id": next_id(),
        "name": name,
        "price": 0,
        "quantity": 0,
        "barcode": barcode,
        "brand": product.get("brands", "")
    }

    inventory.append(item)

    return jsonify({
        "message": "Product imported successfully",
        "item": item
    }), 201


if __name__ == "__main__":
    app.run(debug=True)

