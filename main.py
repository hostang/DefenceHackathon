import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

######
from google.cloud import firestore
from datetime import datetime

app = Flask(__name__)
db = firestore.Client()
COLL = "landingZones"

#####

app = Flask(__name__)
# Wide-open CORS for demo; lock this down to your domain in production.
CORS(app, resources={r"/*": {"origins": "*"}})


from weather import bp as weather_bp
app.register_blueprint(weather_bp, url_prefix="/api")

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/hello/<name>")
def hello_name(name):
    return f"Hello, {name}!"

##########

@app.route("/landingZones/<lz_id>", methods=["GET"])
def get_location(lz_id):
    snap = db.collection(COLL).document(lz_id).get()
    if not snap.exists:
        abort(404)
    d = snap.to_dict()
    d["id"] = lz_id
    d["created_at"] = to_iso(d.get("created_at"))
    d["updated_at"] = to_iso(d.get("updated_at"))
    return jsonify(d)

######

if __name__ == "__main__":
    # For local dev; Cloud Run injects $PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
