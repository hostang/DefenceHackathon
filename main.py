import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
# Wide-open CORS for demo; lock this down to your domain in production.
CORS(app, resources={r"/*": {"origins": "*"}})

# In-memory demo data (swap with DB/BigQuery/etc.)
ITEMS = [
    {"id": 1, "name": "apple", "price": 0.99},
    {"id": 2, "name": "banana", "price": 0.49},
    {"id": 3, "name": "cherry", "price": 2.99},
]

def now_iso():
    return datetime.now(timezone.utc).isoformat()

@app.route("/healthz", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": now_iso()}), 200

@app.route("/api/v1/items", methods=["GET"])
def list_items():
    """
    GET /api/v1/items?min_price=0.5&max_price=2.0&q=an
    """
    q = (request.args.get("q") or "").lower().strip()
    try:
        min_price = float(request.args.get("min_price")) if request.args.get("min_price") else None
        max_price = float(request.args.get("max_price")) if request.args.get("max_price") else None
    except ValueError:
        abort(400, description="min_price and max_price must be numbers")

    results = ITEMS
    if q:
        results = [x for x in results if q in x["name"].lower()]
    if min_price is not None:
        results = [x for x in results if x["price"] >= min_price]
    if max_price is not None:
        results = [x for x in results if x["price"] <= max_price]

    return jsonify({"count": len(results), "items": results}), 200

@app.route("/api/v1/items/<int:item_id>", methods=["GET"])
def get_item(item_id: int):
    item = next((x for x in ITEMS if x["id"] == item_id), None)
    if not item:
        abort(404, description=f"Item {item_id} not found")
    return jsonify(item), 200

@app.route("/api/v1/items", methods=["POST"])
def create_item():
    """
    POST /api/v1/items
    Body: { "name": "orange", "price": 1.25 }
    """
    if not request.is_json:
        abort(400, description="Expected JSON body")
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    price = data.get("price")

    if not name or not isinstance(price, (int, float)):
        abort(400, description="Fields 'name' (str) and 'price' (number) are required")

    new_id = max([x["id"] for x in ITEMS] or [0]) + 1
    item = {"id": new_id, "name": name, "price": float(price)}
    ITEMS.append(item)
    return jsonify(item), 201

@app.route("/api/v1/stats", methods=["GET"])
def stats():
    total = len(ITEMS)
    avg_price = round(sum(x["price"] for x in ITEMS) / total, 2) if total else 0.0
    return jsonify({"total": total, "avg_price": avg_price}), 200

@app.errorhandler(400)
def handle_400(e):
    return jsonify(error="bad_request", message=str(e.description)), 400

@app.errorhandler(404)
def handle_404(e):
    return jsonify(error="not_found", message=str(e.description)), 404

@app.errorhandler(500)
def handle_500(e):
    return jsonify(error="internal_error", message="Something went wrong"), 500

if __name__ == "__main__":
    # For local dev; Cloud Run injects $PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
