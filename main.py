import os
from flask import Flask, request, jsonify
from google.cloud import firestore

from flask_cors import CORS


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firestore DB client

db = firestore.Client()

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

# --- Flask Routes your API endpoints ---

@app.route('/')
# simple test of the routes
def hello_world():
    return 'Hello from Cloud Run Flask App!'

@app.route('/firestore/document/<collection_name>/<document_id>', methods=['GET'])
def get_firestore_document(collection_name, document_id):
    """
    Retrieves a single document from Firestore.
    Example: GET /firestore/document/landingZones/id
    """
    doc_data = get_document(collection_name, document_id)
    if doc_data:
        return jsonify(doc_data), 200
    else:
        return jsonify({"error": "Document not found"}), 404

@app.route('/firestore/collection/<collection_name>', methods=['GET'])
def get_firestore_collection(collection_name):
    """
    Retrieves all documents from a specified collection.
    Example: GET /firestore/collection/landingZones
    """
    collection_data = query_collection(collection_name)
    return jsonify(collection_data), 200

# add more routes for POST (create), PUT/PATCH (update), DELETE operations
# a POST route to create a document:
@app.route('/firestore/document/<collection_name>', methods=['POST'])
def create_firestore_document(collection_name):
    """
    Creates a new document in the specified collection with an auto-generated ID.
    Expects JSON body with the document data.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        update_time, doc_ref = db.collection(collection_name).add(data)
        return jsonify({"message": "Document created", "id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Gunicorn (or similar) will run the app in Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

