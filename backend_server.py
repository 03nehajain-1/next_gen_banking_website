"""
Flask Backend Server for Next Gen Indian Banking Website
Integrates with LangGraph Banking Voice Assistant with Whisper ASR
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import tempfile
import base64

# Add the parent directory to path to import the notebook functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the banking assistant components
try:
    # Import from the updated banking assistant backend with Whisper support
    from banking_assistant_backend import banking_assistant, BankingState
    print("✅ Successfully imported LangGraph banking assistant with Whisper ASR")
except ImportError as e:
    print(f"⚠️  Could not import LangGraph assistant: {e}")
    print("   Will use mock responses mode")
    banking_assistant = None

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Store session data (in production, use Redis or database)
sessions = {}

@app.route('/api/voice-banking', methods=['POST'])
def voice_banking():
    """
    Main endpoint for voice banking queries
    Receives user input (text or audio) and returns AI assistant response
    Supports multilingual responses (English, Hindi, Gujarati)
    Supports Whisper ASR for audio transcription
    """
    try:
        data = request.json
        user_input = data.get('user_input')
        audio_data = data.get('audio_data')  # Base64 encoded audio
        user_id = data.get('user_id')  # Don't default to user_001
        thread_id = data.get('thread_id', f'session_{id(data)}')
        language = data.get('language', 'en')  # en, hi, gu
        
        print(f"🔍 Received request - user_id: {user_id}, language: {language}, input: {user_input[:50] if user_input else 'audio'}")
        
        audio_file_path = None
        
        # Handle audio data if provided
        if audio_data:
            try:
                # Decode base64 audio data
                audio_bytes = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                    temp_audio.write(audio_bytes)
                    audio_file_path = temp_audio.name
                    
                print(f"🎤 Received audio file: {audio_file_path}")
            except Exception as e:
                print(f"❌ Error processing audio data: {e}")
                return jsonify({'error': f'Invalid audio data: {str(e)}'}), 400
        
        if not user_input and not audio_file_path:
            return jsonify({'error': 'No user input or audio provided'}), 400
        
        # If banking_assistant is available, use it
        if banking_assistant:
            initial_state = {
                "user_input": user_input or "",
                "audio_file": audio_file_path,  # Add audio file path for Whisper
                "transcribed_text": None,
                "messages": [],
                "conversation_history": [],
                "is_authenticated": True,  # Assuming user is authenticated via website
                "user_id": user_id,
                "session_token": thread_id,
                "voice_biometric_verified": True,
                "otp_verified": True,
                "security_level": "high",
                "detected_intent": None,
                "intent_confidence": 0.0,
                "entities": {},
                "requires_clarification": False,
                "clarification_question": None,
                "account_number": None,
                "account_balance": None,
                "transaction_history": [],
                "pending_transaction": None,
                "retrieved_context": [],
                "knowledge_base_results": [],
                "response": "",
                "tts_audio": None,
                "next_action": "",
                "current_node": "",
                "error": None,
                "compliance_check_passed": False,
                "language": language  # Add language preference (en, hi, gu)
            }
            
            config = {"configurable": {"thread_id": thread_id}}
            
            # Invoke the LangGraph workflow
            result = banking_assistant.invoke(initial_state, config)
            
            # Clean up temporary audio file
            if audio_file_path and os.path.exists(audio_file_path):
                try:
                    os.unlink(audio_file_path)
                except Exception as e:
                    print(f"⚠️ Could not delete temp audio file: {e}")
            
            # Extract relevant information
            response_data = {
                'response': result.get('response', 'I apologize, but I could not process your request.'),
                'intent': result.get('detected_intent'),
                'confidence': result.get('intent_confidence'),
                'account_balance': result.get('account_balance'),
                'transaction_history': result.get('transaction_history'),
                'entities': result.get('entities'),
                'compliance_passed': result.get('compliance_check_passed'),
                'error': result.get('error')
            }
            
            return jsonify(response_data), 200
        
        else:
            # Mock response if backend is not available
            response_data = generate_mock_response(user_input, user_id)
            return jsonify(response_data), 200
            
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


def generate_mock_response(user_input, user_id):
    """
    Generate mock responses for testing without LangGraph backend
    """
    user_input_lower = user_input.lower()
    
    # Mock user database
    users_db = {
        "user_001": {
            "name": "John Doe",
            "balance": 15750.50,
            "account_number": "ACC123456789"
        }
    }
    
    user_data = users_db.get(user_id, users_db["user_001"])
    user_name = user_data["name"].split()[0]
    
    # Balance inquiry
    if 'balance' in user_input_lower:
        return {
            'response': f"Hello {user_name}, your current account balance is ₹{user_data['balance']:,.2f}. Is there anything else I can help you with?",
            'intent': 'check_balance',
            'confidence': 0.95,
            'account_balance': user_data['balance'],
            'transaction_history': None,
            'entities': {},
            'compliance_passed': True,
            'error': None
        }
    
    # Transaction history
    elif 'transaction' in user_input_lower or 'history' in user_input_lower:
        transactions = [
            {"date": "2025-11-20", "type": "debit", "amount": 150.00, "description": "Grocery Store", "balance": 15750.50},
            {"date": "2025-11-18", "type": "credit", "amount": 3000.00, "description": "Salary Deposit", "balance": 15900.50},
            {"date": "2025-11-15", "type": "debit", "amount": 85.25, "description": "Restaurant", "balance": 12900.50}
        ]
        
        return {
            'response': f"Here are your recent transactions, {user_name}. You had 3 transactions in the last week. Your latest transaction was ₹150 debit at Grocery Store on Nov 20. Would you like more details?",
            'intent': 'view_transactions',
            'confidence': 0.92,
            'account_balance': None,
            'transaction_history': transactions,
            'entities': {},
            'compliance_passed': True,
            'error': None
        }
    
    # Fund transfer
    elif 'transfer' in user_input_lower:
        return {
            'response': f"{user_name}, I can help you transfer funds. Please provide the recipient's account number and the amount you'd like to transfer for security verification.",
            'intent': 'transfer_funds',
            'confidence': 0.88,
            'account_balance': None,
            'transaction_history': None,
            'entities': {},
            'compliance_passed': True,
            'error': None
        }
    
    # Loan inquiry
    elif 'loan' in user_input_lower:
        return {
            'response': f"Hello {user_name}, your current home loan balance is ₹1,20,000 at 7.5% per annum. Your next EMI of ₹8,500 is due on December 5th. Would you like to know more about your loan details?",
            'intent': 'loan_inquiry',
            'confidence': 0.90,
            'account_balance': None,
            'transaction_history': None,
            'entities': {'loan_balance': 120000, 'interest_rate': 7.5},
            'compliance_passed': True,
            'error': None
        }
    
    # Credit card
    elif 'credit' in user_input_lower:
        return {
            'response': f"{user_name}, your credit card limit is ₹50,000 with ₹42,350 available credit. Your current outstanding is ₹7,650 and the payment due date is December 1st. Can I help you with anything else?",
            'intent': 'credit_inquiry',
            'confidence': 0.93,
            'account_balance': None,
            'transaction_history': None,
            'entities': {'credit_limit': 50000, 'available_credit': 42350},
            'compliance_passed': True,
            'error': None
        }
    
    # Default response
    else:
        return {
            'response': f"Hello {user_name}! I'm here to help you with balance inquiries, transaction history, fund transfers, loan information, and credit card details. What would you like to know?",
            'intent': 'general_question',
            'confidence': 0.70,
            'account_balance': None,
            'transaction_history': None,
            'entities': {},
            'compliance_passed': True,
            'error': None
        }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        from banking_assistant_backend import whisper_model
        whisper_available = whisper_model is not None
    except:
        whisper_available = False
    
    return jsonify({
        'status': 'healthy',
        'message': 'Next Gen Indian Banking Voice Assistant is running',
        'service': 'Next Gen Indian Banking Voice Assistant API',
        'version': '1.0.0',
        'whisper_available': whisper_available,
        'langgraph_available': banking_assistant is not None
    }), 200


@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    """
    Authentication endpoint for user login
    """
    from banking_assistant_backend import USERS_DB, TRANSACTIONS_DB
    
    data = request.json
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    # Check credentials
    if username in USERS_DB:
        user = USERS_DB[username]
        if user.get('password') == password:
            # Return user data without password
            user_data = {k: v for k, v in user.items() if k != 'password'}
            return jsonify({
                'success': True,
                'user': user_data,
                'token': f'mock_jwt_token_{username}'
            }), 200
    
    return jsonify({
        'success': False,
        'error': 'Invalid credentials'
    }), 401


@app.route('/api/user/<user_id>', methods=['GET'])
def get_user_data(user_id):
    """
    Get user account data
    """
    from banking_assistant_backend import USERS_DB
    
    user_id = user_id.lower()
    if user_id in USERS_DB:
        user_data = {k: v for k, v in USERS_DB[user_id].items() if k != 'password'}
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
    
    return jsonify({
        'success': False,
        'error': 'User not found'
    }), 404


@app.route('/api/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):
    """
    Get user transaction history
    """
    from banking_assistant_backend import TRANSACTIONS_DB
    
    user_id = user_id.lower()
    if user_id in TRANSACTIONS_DB:
        return jsonify({
            'success': True,
            'transactions': TRANSACTIONS_DB[user_id]
        }), 200
    
    return jsonify({
        'success': False,
        'error': 'No transactions found'
    }), 404


if __name__ == '__main__':
    print("=" * 60)
    print("Next Gen Indian Banking Voice Assistant Backend Server")
    print("=" * 60)
    print("Server starting on http://localhost:8000")
    print("API Endpoint: http://localhost:8000/api/voice-banking")
    print("Health Check: http://localhost:8000/api/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
