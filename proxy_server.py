from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_talisman import Talisman
import requests
import os

app2 = Flask(__name__)
CORS(app2, resources={r"/*": {"origins": "*"}})  # Allow requests from all origins

# Configure Talisman to set security headers
Talisman(app2, content_security_policy=None)

@app2.after_request
def add_cors_headers(response):
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
    return response

@app2.route('/proxy', methods=['POST'])
def proxy():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        headers = [(name, value) for name, value in response.headers.items() if name.lower() not in ['content-length', 'transfer-encoding']]
        return Response(response.raw, headers=headers, content_type=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app2.run(debug=True, host='0.0.0.0', port=port)
