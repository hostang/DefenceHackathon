import os
from flask import Flask, request, jsonify,send_from_directory, render_template
from google.cloud import firestore

from flask_cors import CORS


app = Flask(__name__)

# to avoid Cross Origin Resource sharing issue
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firestore DB client

@app.route("/")
def home():
    return render_template("index.html")  # uses templates/index.html

# Optional: serve static files explicitly (Flask already serves /static/*)
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


if __name__ == '__main__':
    # Gunicorn (or similar) will run the app in Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

