"""
FILE: main.py
Main Flask API server for the LLM Quiz Solver
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from quiz_solver import QuizSolver
import logging
from functools import wraps
import time

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SECRET = os.getenv('SECRET_STRING')
EMAIL = os.getenv('EMAIL')

active_sessions = {}


def verify_secret(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        if data.get('secret') != SECRET:
            logger.warning(f"Invalid secret attempted from {request.remote_addr}")
            return jsonify({'error': 'Invalid secret'}), 403
        
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
            return jsonify({'error': 'Missing email or url'}), 400
        
        # Use email as session key (not email+url, to allow multiple quizzes)
        session_key = email
        
        if session_key not in active_sessions:
            active_sessions[session_key] = {
                'start_time': time.time(),
                'attempts': 0
            }
            logger.info(f"New session: {email}")
        
        elapsed = time.time() - active_sessions[session_key]['start_time']
        if elapsed > 180:
            logger.warning(f"Session timeout for {email}")
            # Reset session if timeout
            active_sessions[session_key] = {
                'start_time': time.time(),
                'attempts': 0
            }
            return jsonify({'error': 'Quiz timeout (3 minutes exceeded)'}), 408
        
        logger.info(f"Processing quiz for {email} - Attempt {active_sessions[session_key]['attempts'] + 1}")
        
        try:
            solver = QuizSolver()
            answer = solver.solve(quiz_url)
            
            logger.info(f"Answer generated: {answer}")
            
            result = solver.submit_answer(
                email=email,
                secret=SECRET,
                url=quiz_url,
                answer=answer
            )
            
            active_sessions[session_key]['attempts'] += 1
            
            logger.info(f"Result: {result}")
            return jsonify(result), 200
        except Exception as solve_error:
            logger.error(f"Error solving quiz: {str(solve_error)}", exc_info=True)
            raise
    
    except Exception as e:
        logger.error(f"Error processing quiz: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    logger.info("Starting Quiz Solver Server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
