# FILE main.py - Main Flask API server for the LLM Quiz Solver
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from quiz_solver import QuizSolver
import logging
from functools import wraps
import time

load_dotenv()

app = Flask(__name__)
logger = logging.getLogger(__name__)

SECRET = os.getenv('SECRET_STRING')
EMAIL = os.getenv('EMAIL')

active_sessions = {}

def verify_secret(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        if data.get('secret') != SECRET:
            return jsonify({"error": "Invalid secret"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/quiz', methods=['POST'])
@verify_secret
def quiz():
    try:
        data = request.get_json()
        email = data.get('email')
        quiz_url = data.get('url')
        
        if not email or not quiz_url:
            return jsonify({"error": "Missing email or url"}), 400
        
        session_key = f"{email}{quiz_url}"
        
        if session_key not in active_sessions:
            active_sessions[session_key] = {"start_time": time.time(), "attempts": 0}
        
        elapsed = time.time() - active_sessions[session_key]["start_time"]
        if elapsed > 180:
            return jsonify({"error": "Quiz timeout (3 minutes) exceeded"}), 408
        
        solver = QuizSolver()
        answer = solver.solve(quiz_url)
        result = solver.submit_answer(email=email, secret=SECRET, url=quiz_url, answer=answer)
        active_sessions[session_key]["attempts"] += 1
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error processing quiz: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
