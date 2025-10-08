import os
from flask import Flask, request, jsonify,send_from_directory, render_template
#from google.cloud import firestore
from google.cloud import bigquery

from flask_cors import CORS


app = Flask(__name__)
bq_client = bigquery.Client()

# to avoid Cross Origin Resource sharing issue
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firestore DB client

@app.route("/")
def home():
    return render_template("index.html")  # uses templates/index.html

# serve static files explicitly
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

#
@app.route("/submit", methods=["POST"])
def submit_form():
    # Get form data
    form_data = request.form.to_dict()

    # Convert latitude & longitude to floats
    row = {
        "lz_id": form_data.get("lz_id"),
        "latitude": float(form_data.get("latitude", 0)),
        "longitude": float(form_data.get("longitude", 0)),
    }
    return jsonify({"success": True, "inserted": row}), 201


if __name__ == '__main__':
    # Gunicorn (or similar) will run the app in Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

