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

"""
########
@app.route('/')
# simple test of the routes
def hello_world():
    return 'Hello from Cloud Run Flask App!'
###########



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
    URL: GET /firestore/document/landingZones/id
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
    URL: GET /firestore/collection/landingZones
    """
    collection_data = query_collection(collection_name)
    return jsonify(collection_data), 200

# add more routes for POST (create), PUT/PATCH (update), DELETE operations
# a POST route to create a document:
@app.route('/firestore/document/<collection_name>', methods=['POST'])
def create_firestore_document(collection_name):
    """
    Creates a new document in firestore with an auto-generated ID.
    PostCondition: Expects JSON body with the document data.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    try:
        update_time, doc_ref = db.collection(collection_name).add(data)
        return jsonify({"message": "Document created", "id": doc_ref.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# return unique set of locations
@app.route('/api/locations', methods=['GET'])
def get_unique_locations():
    """
    Returns a list of unique location names from all documents in Firestore.
    """
    locations = set()
    for doc in db.collection('landingZones').stream():
        data = doc.to_dict()
        loc = data.get('location')
        if loc:
            locations.add(loc)
    return jsonify(sorted(list(locations)))

# filter based on landingZones location
@app.route('/api/landingzones', methods=['GET'])
def get_landing_zones_by_location():
    """
    Returns all landing zone documents that match the given location.
    endpoint URL - /api/landingzones?location=Surrey
    """
    location_param = request.args.get('location')
    if not location_param:
        return jsonify({"error": "Missing 'location' query parameter"}), 400

    # Firestore query: filter by location field
    query = db.collection('landingZones').where('location', '==', location_param).stream()

    results = []
    for doc in query:
        data = doc.to_dict()
        # You can filter or rename fields here before returning
        results.append({
            "id": data.get("lz_id", doc.id),
            "location": data.get("location"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            #"terrain_type": data.get("terrain_type"),
            "recommended_status": data.get("recommended_status", False)
        })

    return jsonify(results), 200
"""

if __name__ == '__main__':
    # Gunicorn (or similar) will run the app in Cloud Run.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

