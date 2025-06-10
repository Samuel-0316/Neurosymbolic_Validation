from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
import cohere
import requests
import json
import time
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

    # Generate wrong answer using HTTP POST to local LLM
    print("Generating wrong answer via local LLM (requests)...")
    wrong_answer = ""
    try:
        response = requests.post(
            " https://52b1-49-204-87-250.ngrok-free.app/chat",
            headers={"Content-Type": "application/json"},
            json={
                "question": query,
                "max_tokens": 100,
                "model": "mlx-community/quantized-gemma-2b-it"
            },
            timeout=30
        )
        response.raise_for_status()
        print(f"Raw response from ngrok endpoint: {response.text}")  # Debug print
        wrong_response_json = response.json()
        wrong_answer = wrong_response_json.get('answer')
        if not wrong_answer:
            wrong_answer = wrong_response_json.get('response')
        if not wrong_answer:
            wrong_answer = str(wrong_response_json)
        wrong_answer = wrong_answer.strip()
    except Exception as e:
        print(f"Error calling local LLM: {e}")
        wrong_answer = "[.....]"
    print(f"Generated wrong answer: {wrong_answer}")
    

      # Simulate processing delay

    # Generate correct answer using the LLM, referencing the wrong answer
    print("Generating correct answer with context of wrong answer...")
    correct_prompt = (
        f"User query: {query}\n"
        f"LLM Generated Answer: {wrong_answer}\n"
        "If the above answer is wrong, provide the correct answer.only not even a single word more than that dont even say crrected answer or give any formated outpot keep everything plain text no nee to give any formattings like * / or any thing only plain text and keep as as short as possible. less then the length of the llm generated answer. "
        "If it is correct, confirm it. Give only the correct answer, with no extra text.keep it as short as possible. and please do not include any words, explanation, or extra text. just a small answer. of less length like direct point to point answer "
    )
    correct_response = cohere_client.chat(
        model='command-xlarge-nightly',
        message=correct_prompt
    )
    correct_answer = correct_response.text.strip()
    print(f"Generated correct answer: {correct_answer}")

    # Query for confidence score (numeric only)
    print("Querying confidence score...")
    confidence_prompt = (
        f"For the answer '{correct_answer}' which you gave previously,and answer given by another llm {wrong_answer} "
        "Do not include any words, explanation, or extra text. Only the number,by thinking how confident you are about the correctness of the answer.In case if you find out the first answer contradicts your answer, assign a confidence score less than 0.5" 
    )
    confidence_response = cohere_client.chat(
        model='command-xlarge-nightly',
        message=confidence_prompt
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
    time.sleep(35)
    return jsonify(response_data), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
