from flask import jsonify  # Optional if you prefer pure dict

def hello_world(request):
    name = request.args.get('name', 'World')
    return jsonify({"message": f"Hello, {name}!"})
