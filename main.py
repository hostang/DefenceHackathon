from flask import Request, jsonify

def hello_http(request: Request):
    name = (request.args.get("name")
            or (request.get_json(silent=True) or {}).get("name")
            or "world")
    return jsonify(ok=True, message=f"Hello, {name}!"), 200
