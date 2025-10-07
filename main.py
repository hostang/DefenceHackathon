import os
from datetime import datetime
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from google.cloud import firestore

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # tighten in prod

db = firestore.Client()
COLL = "landingZones"  # make sure this matches your Firestore collection

# Optional: health check
@app.get("/health")
def health():
    return {"ok": True}

# Helper to serialize timestamps
def to_iso(ts):
    return ts.isoformat() if isinstance(ts, datetime) else ts

# Example root routes
@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/hello/<name>")
def hello_name(name):
    return f"Hello, {name}!"

# --- READ one by id ---
@app.get("/locations/<lz_id>")
def get_location(lz_id):
    snap = db.collection(COLL).document(lz_id).get()
    if not snap.exists:
        abort(404, description="Document not found")
    d = snap.to_dict() or {}
    d["id"] = lz_id
    d["created_at"] = to_iso(d.get("created_at"))
    d["updated_at"] = to_iso(d.get("updated_at"))
    return jsonify(d)

# Optional JSON error so you can see the difference between route 404 and doc 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not_found", "detail": getattr(e, "description", "Route not found")}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
