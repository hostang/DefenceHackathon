import os
from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)

# Initialize Firestore DB client
# This client will automatically pick up credentials from the Cloud Run environment
# (service account associated with the Cloud Run service).
db = firestore.Client()

# --- Firestore CRUD Helper Functions (as discussed previously) ---
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

# --- Flask Routes for your API ---

@app.route('/')
def hello_world():
    return 'Hello from Cloud Run Flask App!'

@app.route('/firestore/document/<collection_name>/<document_id>', methods=['GET'])
def get_firestore_document(collection_name, document_id):
    """
    Retrieves a single document from Firestore.
    Example: GET /firestore/document/landingZones/THq09g8GqNDIw6xnSiNP
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

# You can add more routes for POST (create), PUT/PATCH (update), DELETE operations
# For example, a POST route to create a document:
@app.route('/firestore/document/<collection_name>', methods=['POST'])
def create_firestore_document(collection_name):
    """
    Creates a new document in the specified collection with an auto-generated ID.
    Expects JSON body with the document data.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    # Assuming you have a create_document_auto_id function
    # For simplicity, let's just use .add() directly here
    try:
        update_time, doc_ref = db.collection(collection_name).add(data)
        return jsonify({"message": "Document created", "id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn (or similar) will run the app in Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

