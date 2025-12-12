#!/usr/bin/env python3
"""
Simple Flask server to serve the frontend and proxy Solr requests.
This avoids CORS issues when the frontend tries to access Solr directly.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import sys
import os
from pathlib import Path

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)

SOLR_BASE_URL = "http://localhost:8983/solr"

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Skip API routes
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory(BASE_DIR, path)

@app.route('/api/search', methods=['POST'])
def search():
    """
    Proxy endpoint to query Solr and return results.
    Expects JSON body with: core, params
    """
    try:
        data = request.json
        core = data.get('core', 'songs')
        params = data.get('params', {})
        
        solr_url = f"{SOLR_BASE_URL}/{core}/select"
        
        # Make request to Solr
        response = requests.post(
            solr_url,
            data=params,
            timeout=10
        )
        response.raise_for_status()
        
        return jsonify(response.json())
    
    except requests.RequestException as e:
        return jsonify({
            'error': f'Solr request failed: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🎵 Music Search Frontend Server")
    print("=" * 60)
    print(f"Frontend: http://localhost:5000")
    print(f"Solr URL: {SOLR_BASE_URL}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
