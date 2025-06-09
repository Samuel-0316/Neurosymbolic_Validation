from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
import cohere

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Initialize Cohere client
cohere_client = cohere.Client("6GnWnaNLQGhHdV4uN7viA5OQoR8pRWGlG6KvXedS")

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

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.json
    if not data or 'query' not in data:
        print("POST /api/query route called - Invalid query format")
        return jsonify({"error": "Query is required"}), 400

    query = data['query']
    print(f"Received query: {query}")

    # Generate wrong answer using the LLM
    print("Generating wrong answer...")
    wrong_response = cohere_client.chat(
        model='command-xlarge-nightly',
        message=f"Give a strictly wrong answer to this question, with no explanation or extra text just the wrong answer  keep srtictly in mind no matter what happens and  not like any jokes : {query}"
    )
    wrong_answer = wrong_response.text.strip()
    print(f"Generated wrong answer: {wrong_answer}")

    # Generate correct answer using the LLM
    print("Generating correct answer...")
    correct_response = cohere_client.chat(
        model='command-xlarge-nightly',
        message=f"Give the correct answer to this question, with no extra text: {query}"
    )
    correct_answer = correct_response.text.strip()
    print(f"Generated correct answer only answer not even a single Character more than the answer keep srtictly in mind no matter what happens : {correct_answer}")

    # Query for confidence score (numeric only)
    print("Querying confidence score...")
    confidence_response = cohere_client.chat(
        model='command-xlarge-nightly',
        message=f"For the answer '{correct_answer}', give only a confidence score as a number between 0 and 1. Do not include any words, explanation, or extra text. Only the number so that i can get how truth is this you have to give number no text at all other than that."
    )
    confidence_score = confidence_response.text.strip()
    print(f"Confidence score: {confidence_score}")

    # Combine results into a single response
    response_data = {
        "wrong_answer": wrong_answer,
        "correct_answer": correct_answer,
        "confidence_score": confidence_score
    }
    print(f"Response data: {response_data}")

    return jsonify(response_data), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
