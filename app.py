
from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

# Temporary inventory storage.
inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "price": 350.00,
        "quantity": 10,
        "barcode": "3017620422003",
        "brand": "Silk"
    },
    {
        "id": 2,
        "name": "Whole Wheat Bread",
        "price": 120.00,
        "quantity": 20,
        "barcode": "",
        "brand": "Local Bakery"
    }
]


def find_item(item_id):
    """Find an item using its ID."""
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None


def next_item_id():
    """Generate the next available inventory ID."""
    return max((item["id"] for item in inventory), default=0) + 1


def fetch_product(url, params=None):
    """Fetch product information from OpenFoodFacts."""
    response = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "InventoryManagementStudentProject/1.0"
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Inventory Management API"
    }), 200


# GET: View all inventory items.
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


# GET: View one inventory item.
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item), 200


# POST: Add a new inventory item.
@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Please send valid JSON"}), 400

    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Item name is required"}), 400

    if (
        isinstance(price, bool)
        or not isinstance(price, (int, float))
        or price < 0
    ):
        return jsonify({"error": "Price must be a non-negative number"}), 400

    if (
        isinstance(quantity, bool)
        or not isinstance(quantity, int)
        or quantity < 0
    ):
        return jsonify({
            "error": "Quantity must be a non-negative integer"
        }), 400

    barcode = data.get("barcode", "")
    brand = data.get("brand", "")

    if not isinstance(barcode, str) or not isinstance(brand, str):
        return jsonify({
            "error": "Barcode and brand must be text"
        }), 400

    new_item = {
        "id": next_item_id(),
        "name": name.strip(),
        "price": price,
        "quantity": quantity,
        "barcode": barcode.strip(),
        "brand": brand.strip()
    }

    inventory.append(new_item)

    return jsonify(new_item), 201


# PATCH: Update an existing inventory item.
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Please provide valid update data"
        }), 400

    allowed_fields = ["name", "price", "quantity", "barcode", "brand"]

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"Cannot update field: {field}"
            }), 400

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return jsonify({"error": "Name must not be empty"}), 400

    if "price" in data:
        price = data["price"]
        if (
            isinstance(price, bool)
            or not isinstance(price, (int, float))
            or price < 0
        ):
            return jsonify({
                "error": "Price must be a non-negative number"
            }), 400

    if "quantity" in data:
        quantity = data["quantity"]
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 0
        ):
            return jsonify({
                "error": "Quantity must be a non-negative integer"
            }), 400

    for field in ["barcode", "brand"]:
        if field in data and not isinstance(data[field], str):
            return jsonify({
                "error": f"{field} must be text"
            }), 400

    # Update only the fields supplied by the user.
    for field, value in data.items():
        item[field] = value.strip() if field in ["name", "barcode", "brand"] else value

    return jsonify(item), 200


# DELETE: Remove an inventory item.
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)

    return "", 204


# GET: Find a product using its barcode.
@app.route("/external/barcode/<barcode>", methods=["GET"])
def find_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    try:
        result = fetch_product(url)

    except (requests.RequestException, ValueError):
        return jsonify({
            "error": "Could not fetch product data"
        }), 502

    if result.get("status") != 1:
        return jsonify({
            "error": "Product not found on OpenFoodFacts"
        }), 404

    product = result.get("product", {})

    return jsonify({
        "barcode": barcode,
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
        "quantity": product.get("quantity", "")
    }), 200


# GET: Search OpenFoodFacts by product name.
@app.route("/external/search", methods=["GET"])
def search_product():
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({
            "error": "Please provide a product name"
        }), 400

    url = "https://world.openfoodfacts.org/cgi/search.pl"

    try:
        result = fetch_product(
            url,
            params={
                "search_terms": name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 5
            }
        )

    except (requests.RequestException, ValueError):
        return jsonify({
            "error": "Could not search OpenFoodFacts"
        }), 502

    products = []

    for product in result.get("products", []):
        products.append({
            "name": product.get("product_name", ""),
            "brand": product.get("brands", ""),
            "barcode": product.get("code", ""),
            "ingredients": product.get("ingredients_text", "")
        })

    return jsonify(products), 200


# POST: Fetch a product and add it to inventory.
@app.route("/external/import/<barcode>", methods=["POST"])
def import_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    try:
        result = fetch_product(url)

    except (requests.RequestException, ValueError):
        return jsonify({
            "error": "Could not fetch product data"
        }), 502

    if result.get("status") != 1:
        return jsonify({"error": "Product not found"}), 404

    product = result.get("product", {})
    name = product.get("product_name", "").strip()

    if not name:
        return jsonify({
            "error": "Product has no name"
        }), 422

    # Do not import the same barcode twice.
    for item in inventory:
        if item["barcode"] == barcode:
            return jsonify({
                "message": "Product is already in inventory",
                "item": item
            }), 200

    new_item = {
        "id": next_item_id(),
        "name": name,
        "price": 0,
        "quantity": 0,
        "barcode": barcode,
        "brand": product.get("brands", "")
    }

    inventory.append(new_item)

    return jsonify({
        "message": "Product imported successfully",
        "item": new_item
    }), 201


if __name__ == "__main__":
    app.run(debug=True)