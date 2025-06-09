from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Temporary storage for messages (replace with database later)
messages = []

@app.route('/api/messages', methods=['GET'])
def get_messages():
    print("GET /api/messages route called - Retrieving all messages")
    return jsonify(messages)

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    if not data or 'message' not in data or 'user' not in data:
        print("POST /api/messages route called - Invalid message format")
        return jsonify({"error": "Invalid message format"}), 400
    
    new_message = {
        'user': data['user'],
        'message': data['message'],
        'timestamp': str(datetime.now())
    }
    messages.append(new_message)
    print(f"POST /api/messages route called - Message sent by {data['user']}")
    return jsonify(new_message), 201

@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data:
        print("POST /api/users/login route called - Invalid login attempt")
        return jsonify({"error": "Username is required"}), 400
    
    print(f"POST /api/users/login route called - User {data['username']} logged in")
    return jsonify({"message": "Login successful", "username": data['username']})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
