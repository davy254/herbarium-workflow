from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app) 

API_KEY = "sk-mr-3c4d1d7c7bc043b6dcab8d40f8e523263fca0fb515611275370141962985fb3a"
API_URL = "https://api.mulerouter.ai/vendors/openai/v1/chat/completions"

@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    data = request.json
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Debug: Show what model is being requested
    print(f"\n--- Sending request to MuleRouter ---")
    print(f"Model requested: {data.get('model')}")
    
    # Forward the request to MuleRouter
    response = requests.post(API_URL, json=data, headers=headers)
    
    # Debug: Print exactly what MuleRouter returned
    print(f"MuleRouter Status Code: {response.status_code}")
    print(f"MuleRouter Raw Response: {response.text[:500]}") 
    print("---------------------------------------\n")
    
    # Try to parse the response as JSON
    try:
        return jsonify(response.json()), response.status_code
    except requests.exceptions.JSONDecodeError:
        # If MuleRouter returned HTML or plain text instead of JSON, catch it!
        print("❌ ERROR: MuleRouter did not return valid JSON!")
        return jsonify({
            "error": "Invalid response from MuleRouter",
            "status_code": response.status_code,
            "details": response.text
        }), response.status_code

if __name__ == '__main__':
    print("✅ Backend server running on port 5000")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
