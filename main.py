import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
# Wide-open CORS for demo; lock this down to your domain in production.
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/hello/<name>")
def hello_name(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    # For local dev; Cloud Run injects $PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
