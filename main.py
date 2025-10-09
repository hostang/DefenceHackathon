import os
from flask import Flask, request, jsonify,send_from_directory, render_template
from google.cloud import firestore
from google.cloud import bigquery
from datetime import datetime


from flask_cors import CORS


app = Flask(__name__)
bq_client = bigquery.Client()

db = firestore.Client()

# to avoid Cross Origin Resource sharing issue
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Firestore CRUD Helper Functions ---
def get_document(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
        
def query_collection(collection_name):
    docs = db.collection(collection_name).stream()
    return [doc.to_dict() for doc in docs]
# global variable
latest_doc_id = None

# --- Flask Firestore Routes API endpoints ---
@app.route("/firestore/document/<collection_name>/<document_id>", methods=["GET"])
def get_firestore_document(collection_name, document_id):
    """
    Retrieves a single document from Firestore.
    URL: GET /firestore/document/landingZones/id
    """
    doc_data = get_document(collection_name, document_id)
    if doc_data:
        return jsonify(doc_data), 200
    else:
        return jsonify({"error": "Document not found"}), 404

@app.route("/firestore/document/<collection_name>/latest", methods=["GET"])
def get_latest_document(collection_name):
    try:
        q = (db.collection(collection_name)
               .order_by("created_at", direction=firestore.Query.DESCENDING)
               .limit(1))
        docs = list(q.stream())
        if not docs:
            return jsonify({"error": "No documents found"}), 404
        snap = docs[0]
        return jsonify({"id": snap.id, **snap.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# add more routes for POST (create), PUT/PATCH (update), DELETE operations
# a POST route to create a document:


@app.route("/firestore/document/<collection_name>", methods=["POST"])
def create_firestore_document(collection_name):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    data["created_at"] = firestore.SERVER_TIMESTAMP
    _, doc_ref = db.collection(collection_name).add(data)
    return jsonify({"message": "Document created", "id": doc_ref.id}), 201
    
'''
@app.route("/firestore/document/<collection_name>", methods=["POST"])
def create_firestore_document(collection_name):
    """
    Creates a new document in firestore with an auto-generated ID.
    PostCondition: Expects JSON body with the document data.
    """
    global latest_doc_id
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        update_time, doc_ref = db.collection(collection_name).add(data)
        latest_doc_id = doc_ref.id
        return jsonify({"message": "Document created", "id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''
@app.route("/")
def home():
    return render_template("index.html")  # uses templates/index.html

@app.route("/report")
def home():
    return render_template("report.html")  # uses templates/index.html

# serve static files explicitly
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# submit to bigquery from POST method of submit
@app.route("/submit", methods=["POST"])
def submit_form():
    # Get form data
    form_data = request.form.to_dict()

    # Convert latitude & longitude to floats
    row = {
        "lz_id": form_data.get("grid_reference"),
        "latitude": float(form_data.get("lat", 0)),
        "longitude": float(form_data.get("lng", 0)),
    }
    # inserting rows to big query
    errors = bq_client.insert_rows_json("mod-hack25swi-393.hlzlandingdata.data",[row])
    if errors:
        return jsonify({"error": errors}),400
    return jsonify({"success": True, "inserted": row}), 201


if __name__ == '__main__':
    # Gunicorn (or similar) will run the app in Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

