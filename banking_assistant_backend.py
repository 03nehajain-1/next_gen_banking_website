"""
Banking Assistant Backend Integration
Exports the LangGraph banking assistant for use with Flask backend

This file uses the exact configuration from 04_banking_voice_assistant.ipynb
"""

import os
from typing import Dict, TypedDict, Annotated, List, Optional
import operator
import json
import random
from datetime import datetime

from dotenv import load_dotenv
import httpx
import whisper

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# Walmart authentication
from walmart_gpa_peopleai_core.auth_sig import generate_auth_sig

load_dotenv()

# ============================================================================
# LLM CONFIGURATION (Exact copy from notebook)
# ============================================================================

print("🔧 Initializing Banking Assistant from Notebook Configuration...")

# Azure OpenAI LLM Configuration
# Load enterprise Walmart LLM gateway settings from environment variables
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
CONSUMER_ID = os.getenv("CONSUMER_ID")
API_VERSION = os.getenv("API_VERSION")
WM_SVC_ENV = os.getenv("WM_SVC_ENV")
LLM_MODEL = os.getenv("LLM_MODEL")

# Validate required environment variables
required_vars = {
    "AZURE_ENDPOINT": AZURE_ENDPOINT,
    "PRIVATE_KEY_PATH": PRIVATE_KEY_PATH,
    "CONSUMER_ID": CONSUMER_ID,
    "API_VERSION": API_VERSION,
    "WM_SVC_ENV": WM_SVC_ENV,
    "LLM_MODEL": LLM_MODEL
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file.")

# Generate Walmart authentication signature
epoch_ts, sig = generate_auth_sig(CONSUMER_ID, PRIVATE_KEY_PATH)
os.environ["OPENAI_API_KEY"] = CONSUMER_ID

# Configure enterprise security headers
headers: Dict[str, str] = {
    "WM_CONSUMER.ID": CONSUMER_ID,
    "WM_SVC.NAME": "WMTLLMGATEWAY", 
    "WM_SVC.ENV": WM_SVC_ENV,
    "WM_SEC.KEY_VERSION": "1",
    "WM_SEC.AUTH_SIGNATURE": sig,
    "WM_CONSUMER.INTIMESTAMP": str(epoch_ts),
    "Content-Type": "application/json",
}

# Create HTTP clients with enterprise auth
client = httpx.Client(verify=False, headers=headers)
async_client = httpx.AsyncClient(verify=False, headers=headers)

# Initialize LLM with enterprise configuration
llm = AzureChatOpenAI(
    openai_api_key=CONSUMER_ID,
    model=LLM_MODEL,
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    http_client=client,
    http_async_client=async_client,
    temperature=0,  # Deterministic responses for routing
)

print("✅ LLM configured and ready")

# ============================================================================
# WHISPER MODEL INITIALIZATION
# ============================================================================

print("🎤 Loading Whisper model for speech recognition...")
try:
    whisper_model = whisper.load_model("tiny")  # Using "tiny" for fastest loading
    print("✅ Whisper model loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load Whisper model: {e}")
    whisper_model = None

# ============================================================================
# STATE DEFINITION
# ============================================================================

class BankingState(TypedDict):
    """State schema for the banking voice assistant"""
    
    # User input and conversation
    user_input: str
    audio_file: Optional[str]  # Path to audio file for Whisper transcription
    transcribed_text: Optional[str]
    messages: Annotated[List[BaseMessage], operator.add]
    conversation_history: List[str]
    language: str  # Language preference: 'en', 'hi', 'gu'
    
    # Authentication and security
    is_authenticated: bool
    user_id: Optional[str]
    session_token: Optional[str]
    voice_biometric_verified: bool
    otp_verified: bool
    security_level: str
    
    # Intent and context
    detected_intent: Optional[str]
    intent_confidence: float
    entities: Dict[str, any]
    requires_clarification: bool
    clarification_question: Optional[str]
    
    # Banking operations
    account_number: Optional[str]
    account_balance: Optional[float]
    transaction_history: List[Dict]
    pending_transaction: Optional[Dict]
    
    # RAG context
    retrieved_context: List[str]
    knowledge_base_results: List[Dict]
    
    # Response generation
    response: str
    tts_audio: Optional[str]
    
    # Flow control
    next_action: str
    current_node: str
    error: Optional[str]
    compliance_check_passed: bool


# ============================================================================
# MOCK DATA - Next Gen Bank Users
# ============================================================================

USERS_DB = {
    "neha": {
        "user_id": "neha",
        "password": "neha123",
        "name": "Neha Sharma",
        "account_number": "NGB001234567890",
        "balance": 125000.00,
        "voice_signature": "verified",
        "phone": "+91-9876543210",
        "email": "neha.sharma@email.com",
        "address": "101, Prestige Apartments, Koramangala, Bangalore - 560034",
        "account_type": "Savings Account",
        "ifsc_code": "NXGB0001234",
        "branch": "Koramangala Branch, Bangalore",
        "date_opened": "2020-03-15",
        "pan": "ABCPN1234D",
        "aadhar": "****-****-5678",
        "credit_limit": 200000.00,
        "loan_balance": 180000.00,
        "interest_rate": 7.5,
        "cards": [
            {
                "type": "Debit Card",
                "number": "****-****-****-1234",
                "expiry": "12/2026"
            },
            {
                "type": "Credit Card - Next Gen SimplyCLICK",
                "number": "****-****-****-5678",
                "expiry": "08/2027",
                "limit": 200000,
                "outstanding": 15000
            }
        ]
    },
    "niyati": {
        "user_id": "niyati",
        "password": "niyati123",
        "name": "Niyati Patel",
        "account_number": "NGB009876543210",
        "balance": 87500.00,
        "voice_signature": "verified",
        "phone": "+91-9123456789",
        "email": "niyati.patel@email.com",
        "address": "204, Sunrise Heights, Satellite Road, Ahmedabad - 380015",
        "account_type": "Savings Account",
        "ifsc_code": "NXGB0009876",
        "branch": "Satellite Branch, Ahmedabad",
        "date_opened": "2019-07-22",
        "pan": "DEFPN5678K",
        "aadhar": "****-****-9012",
        "credit_limit": 150000.00,
        "loan_balance": 4120000.00,
        "interest_rate": 8.25,
        "cards": [
            {
                "type": "Debit Card",
                "number": "****-****-****-9012",
                "expiry": "06/2027"
            },
            {
                "type": "Credit Card - Next Gen Card PRIME",
                "number": "****-****-****-3456",
                "expiry": "03/2028",
                "limit": 150000,
                "outstanding": 8500
            }
        ]
    }
}

TRANSACTIONS_DB = {
    "neha": [
        {"date": "2025-11-22", "type": "credit", "amount": 75000.00, "description": "Salary Credit - Tech Corp", "balance": 125000.00},
        {"date": "2025-11-20", "type": "debit", "amount": 12500.00, "description": "Personal Loan EMI", "balance": 50000.00},
        {"date": "2025-11-18", "type": "debit", "amount": 3500.00, "description": "Amazon - Electronics", "balance": 62500.00},
        {"date": "2025-11-15", "type": "credit", "amount": 5000.00, "description": "IMPS Transfer from Mother", "balance": 66000.00},
        {"date": "2025-11-12", "type": "debit", "amount": 15000.00, "description": "Credit Card Payment", "balance": 61000.00},
        {"date": "2025-11-10", "type": "debit", "amount": 8000.00, "description": "Big Bazaar - Groceries", "balance": 76000.00},
        {"date": "2025-11-08", "type": "debit", "amount": 2500.00, "description": "BESCOM Electricity Bill", "balance": 84000.00},
        {"date": "2025-11-05", "type": "debit", "amount": 4500.00, "description": "Truffles Restaurant", "balance": 86500.00},
        {"date": "2025-11-03", "type": "credit", "amount": 12000.00, "description": "Freelance Project Payment", "balance": 91000.00},
        {"date": "2025-11-01", "type": "debit", "amount": 18000.00, "description": "Monthly Rent", "balance": 79000.00},
    ],
    "niyati": [
        {"date": "2025-11-22", "type": "credit", "amount": 95000.00, "description": "Salary Credit - InfoTech Ltd", "balance": 87500.00},
        {"date": "2025-11-21", "type": "debit", "amount": 35000.00, "description": "Home Loan EMI", "balance": -7500.00},
        {"date": "2025-11-20", "type": "debit", "amount": 18000.00, "description": "Car Loan EMI", "balance": 27500.00},
        {"date": "2025-11-18", "type": "debit", "amount": 6500.00, "description": "Delhi Public School Fees", "balance": 63500.00},
        {"date": "2025-11-16", "type": "debit", "amount": 8500.00, "description": "Credit Card Payment", "balance": 70000.00},
        {"date": "2025-11-14", "type": "debit", "amount": 12000.00, "description": "Reliance Fresh - Monthly Grocery", "balance": 78500.00},
        {"date": "2025-11-12", "type": "credit", "amount": 15000.00, "description": "Mutual Fund Dividend", "balance": 90500.00},
        {"date": "2025-11-10", "type": "debit", "amount": 3500.00, "description": "Adani Gas Bill", "balance": 75500.00},
        {"date": "2025-11-08", "type": "debit", "amount": 5000.00, "description": "Apollo Pharmacy", "balance": 79000.00},
        {"date": "2025-11-05", "type": "debit", "amount": 25000.00, "description": "LIC Premium Payment", "balance": 84000.00},
    ]
}

KNOWLEDGE_BASE = [
    {"topic": "interest_rates", "content": "Current savings account interest rate is 2.5% per annum. Home loan rates start at 7.25% for qualified borrowers with flexible repayment options."},
    {"topic": "credit_cards", "content": "We offer credit cards with 0% introductory interest for 12 months, rewards programs, cashback benefits, and no annual fees for the first year."},
    {"topic": "transfer_limits", "content": "Daily NEFT/RTGS transfer limit is ₹5,00,000 for verified accounts. IMPS transfers have a limit of ₹2,00,000. International transfers may take 2-5 business days."},
]


# ============================================================================
# AGENT NODES
# ============================================================================

def speech_agent(state: BankingState) -> BankingState:
    """Speech Agent: Handles voice input transcription using Whisper"""
    
    # Check if audio file path is provided
    audio_file = state.get("audio_file")
    
    if audio_file and whisper_model:
        # Use Whisper to transcribe audio file
        try:
            language = state.get("language", "en")
            # Map language codes to Whisper format
            whisper_lang = None if language == "auto" else language
            
            print(f"🎤 Transcribing audio with Whisper (language: {whisper_lang or 'auto-detect'})...")
            result = whisper_model.transcribe(audio_file, language=whisper_lang)
            transcribed = result["text"].strip()
            detected_lang = result.get("language", language)
            
            print(f"✅ ASR text: {transcribed}")
            print(f"✅ Detected language: {detected_lang}")
            
            new_messages = []
            if not state.get('messages') or not any(
                isinstance(msg, HumanMessage) and msg.content == transcribed 
                for msg in state.get('messages', [])
            ):
                new_messages.append(HumanMessage(content=transcribed))
            
            return {
                **state,
                "transcribed_text": transcribed,
                "messages": new_messages,
                "current_node": "speech",
                "next_action": "understand_intent",
                "language": detected_lang  # Update with detected language
            }
        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            return {
                **state,
                "error": f"Audio transcription failed: {str(e)}",
                "current_node": "speech",
                "next_action": "end"
            }
    
    # Fallback: Use text input directly
    elif state.get("user_input"):
        transcribed = state["user_input"]
        new_messages = []
        if not state.get('messages') or not any(
            isinstance(msg, HumanMessage) and msg.content == transcribed 
            for msg in state.get('messages', [])
        ):
            new_messages.append(HumanMessage(content=transcribed))
        
        return {
            **state,
            "transcribed_text": transcribed,
            "messages": new_messages,
            "current_node": "speech",
            "next_action": "understand_intent"  # Skip auth for web users
        }
    else:
        return {
            **state,
            "error": "No input detected",
            "current_node": "speech",
            "next_action": "end"
        }


def intent_understanding_agent(state: BankingState) -> BankingState:
    """Intent Understanding Agent: Detects user intent - Multilingual support"""
    user_text = state.get("transcribed_text", "")
    language = state.get("language", "en")
    
    print(f"🔍 Intent Agent - User text: '{user_text}', Language: {language}")
    
    # Language-specific prompts
    if language == "hi":
        intent_prompt = f"""
आप एक बैंकिंग सहायक के लिए इंटेंट क्लासिफायर हैं। उपयोगकर्ता के अनुरोध का विश्लेषण करें और पहचानें:
1. मुख्य इंटेंट (इनमें से एक: check_balance, view_transactions, transfer_funds, make_payment, loan_inquiry, credit_inquiry, general_question)
2. विश्वास स्तर (0.0 से 1.0)
3. एंटिटीज (राशि, तारीख, खाता संख्या)

उपयोगकर्ता का अनुरोध: "{user_text}"

JSON फॉर्मेट में जवाब दें:
{{
    "intent": "<intent_name>",
    "confidence": <float>,
    "entities": {{}}
}}
"""
    elif language == "gu":
        intent_prompt = f"""
તમે બેન્કિંગ આસિસ્ટન્ટ માટે ઇન્ટેન્ટ ક્લાસિફાયર છો. યુઝરની વિનંતીનું વિશ્લેષણ કરો અને ઓળખો:
1. મુખ્ય ઇન્ટેન્ટ (આમાંથી એક: check_balance, view_transactions, transfer_funds, make_payment, loan_inquiry, credit_inquiry, general_question)
2. વિશ્વાસ સ્તર (0.0 થી 1.0)
3. એન્ટિટીઝ (રકમ, તારીખ, ખાતા નંબર)

યુઝરની વિનંતી: "{user_text}"

JSON ફોર્મેટમાં જવાબ આપો:
{{
    "intent": "<intent_name>",
    "confidence": <float>,
    "entities": {{}}
}}
"""
    else:  # English
        intent_prompt = f"""
You are an intent classifier for a banking assistant. Analyze the user's request and identify:
1. Primary intent (one of: check_balance, view_transactions, transfer_funds, make_payment, loan_inquiry, credit_inquiry, general_question)
2. Confidence level (0.0 to 1.0)
3. Entities (amounts, dates, account numbers)

User request: "{user_text}"

Respond in JSON format:
{{
    "intent": "<intent_name>",
    "confidence": <float>,
    "entities": {{}}
}}
"""
    
    try:
        print(f"🤖 Calling LLM for intent classification...")
        response = llm.invoke(intent_prompt)
        print(f"🤖 LLM raw response: {response.content}")
        result = json.loads(response.content)
        
        print(f"✅ Detected intent: {result['intent']} (confidence: {result['confidence']})")
        
        return {
            **state,
            "detected_intent": result["intent"],
            "intent_confidence": result["confidence"],
            "entities": result.get("entities", {}),
            "current_node": "intent",
            "next_action": "retrieve_context"
        }
    except Exception as e:
        print(f"❌ Intent detection error: {e}")
        print(f"🔄 Falling back to keyword-based intent detection...")
        
        # Fallback: keyword-based intent detection
        user_text_lower = user_text.lower()
        detected_intent = "general_question"
        confidence = 0.7
        entities = {}
        
        if any(word in user_text_lower for word in ['balance', 'बैलेंस', 'બેલેન્સ']):
            detected_intent = "check_balance"
            confidence = 0.9
        elif any(word in user_text_lower for word in ['transaction', 'history', 'लेनदेन', 'વ્યવહાર']):
            detected_intent = "view_transactions"
            confidence = 0.9
        elif any(word in user_text_lower for word in ['transfer', 'send', 'pay', 'भेजें', 'મોકલો']):
            detected_intent = "transfer_funds"
            confidence = 0.8
            
            # Extract amount and recipient from text
            import re
            # Look for amount patterns like "10000", "10,000", "₹10000"
            amount_match = re.search(r'(?:₹|rupees?|rs\.?)\s*(\d[\d,]*)', user_text_lower)
            if not amount_match:
                amount_match = re.search(r'(\d[\d,]*)\s*(?:rupees?|rs\.?|₹)', user_text_lower)
            if not amount_match:
                # Just look for any number
                amount_match = re.search(r'\b(\d[\d,]*)\b', user_text_lower)
            
            if amount_match:
                entities["amount"] = amount_match.group(1).replace(',', '')
                print(f"✅ Extracted amount: {entities['amount']}")
            
            # Look for recipient name after "to" keyword
            recipient_match = re.search(r'to\s+([a-zA-Z]+)', user_text_lower)
            if recipient_match:
                entities["recipient"] = recipient_match.group(1).capitalize()
                print(f"✅ Extracted recipient: {entities['recipient']}")
            
        elif any(word in user_text_lower for word in ['loan', 'लोन', 'લોન', 'emi']):
            detected_intent = "loan_inquiry"
            confidence = 0.9
        elif any(word in user_text_lower for word in ['credit', 'card', 'क्रेडिट', 'ક્રેડિટ']):
            detected_intent = "credit_inquiry"
            confidence = 0.9
        
        print(f"✅ Fallback detected intent: {detected_intent} (confidence: {confidence})")
        if entities:
            print(f"✅ Extracted entities: {entities}")
        
        return {
            **state,
            "detected_intent": detected_intent,
            "intent_confidence": confidence,
            "entities": entities,
            "current_node": "intent",
            "next_action": "retrieve_context",
            "error": None  # Clear error since we have a fallback
        }


def rag_retrieval_agent(state: BankingState) -> BankingState:
    """RAG Retrieval Agent: Retrieves relevant context"""
    intent = state.get("detected_intent", "")
    
    intent_topic_map = {
        "loan_inquiry": ["interest_rates"],
        "credit_inquiry": ["credit_cards"],
        "transfer_funds": ["transfer_limits"],
    }
    
    topics = intent_topic_map.get(intent, [])
    relevant_docs = [doc["content"] for doc in KNOWLEDGE_BASE if doc["topic"] in topics]
    
    return {
        **state,
        "retrieved_context": relevant_docs,
        "current_node": "rag",
        "next_action": "execute_banking"
    }


def banking_operations_agent(state: BankingState) -> BankingState:
    """Banking Operations Agent: Executes banking operations"""
    intent = state.get("detected_intent")
    user_id = state.get("user_id")
    
    print(f"🔍 Banking Operations - Intent: {intent}, User ID: {user_id}")
    
    if not user_id or user_id not in USERS_DB:
        print(f"❌ User not authenticated or not found: {user_id}")
        return {
            **state,
            "error": "User not authenticated",
            "next_action": "respond"
        }
    
    user_data = USERS_DB[user_id]
    print(f"✅ Found user data for {user_data['name']}: Balance = ₹{user_data['balance']:,.2f}")
    
    # Ensure entities dict exists
    if "entities" not in state or state["entities"] is None:
        state["entities"] = {}
    
    if intent == "check_balance":
        state["account_balance"] = user_data["balance"]
        state["account_number"] = user_data["account_number"]
        print(f"✅ Set account_balance = ₹{state['account_balance']:,.2f}, account_number = {state['account_number']}")
    elif intent == "view_transactions":
        state["transaction_history"] = TRANSACTIONS_DB.get(user_id, [])[:5]
        state["account_number"] = user_data["account_number"]
        print(f"✅ Set {len(state['transaction_history'])} transactions")
    elif intent == "loan_inquiry":
        # Create a new entities dict with loan information
        entities = dict(state.get("entities", {}))
        entities["loan_balance"] = user_data.get("loan_balance", 0)
        entities["interest_rate"] = user_data.get("interest_rate", 0)
        entities["name"] = user_data.get("name", "")
        state["entities"] = entities
        state["account_number"] = user_data["account_number"]
        print(f"✅ Set loan_balance = ₹{entities['loan_balance']:,.2f}, interest_rate = {entities['interest_rate']}%")
    elif intent == "credit_inquiry":
        # Create a new entities dict with credit information
        entities = dict(state.get("entities", {}))
        entities["credit_limit"] = user_data.get("credit_limit", 0)
        entities["cards"] = user_data.get("cards", [])
        state["entities"] = entities
        state["account_number"] = user_data["account_number"]
        print(f"✅ Set credit_limit = ₹{entities['credit_limit']:,.2f}")
    elif intent == "transfer_funds":
        # Handle fund transfer request
        entities = dict(state.get("entities", {}))
        amount = entities.get("amount", 0)
        recipient = entities.get("recipient", "").lower().strip()
        
        print(f"🔍 Transfer request - Amount: {amount}, Recipient: {recipient}")
        
        # Convert amount to float if it's a string
        try:
            amount = float(str(amount).replace(",", "").replace("₹", ""))
        except (ValueError, TypeError):
            print(f"❌ Invalid amount: {amount}")
            state["error"] = "Invalid transfer amount"
            state["next_action"] = "respond"
            return state
        
        # Check if recipient exists - match by full name, first name, or user ID
        recipient_data = None
        recipient_id = None
        for uid, udata in USERS_DB.items():
            # Skip if trying to transfer to self
            if uid == user_id:
                continue
            
            full_name = udata["name"].lower()
            first_name = full_name.split()[0]
            
            # Match by full name, first name, or user ID
            if full_name == recipient or first_name == recipient or uid == recipient:
                recipient_data = udata
                recipient_id = uid
                print(f"✅ Found recipient: {udata['name']} (ID: {uid})")
                break
        
        if not recipient_data:
            print(f"❌ Recipient not found: {recipient}")
            entities["error"] = "Recipient not found"
            state["entities"] = entities
            state["account_number"] = user_data["account_number"]
            state["next_action"] = "generate_response"
        elif amount <= 0:
            print(f"❌ Invalid amount: {amount}")
            entities["error"] = "Invalid transfer amount"
            state["entities"] = entities
            state["account_number"] = user_data["account_number"]
            state["next_action"] = "generate_response"
        elif user_data["balance"] < amount:
            print(f"❌ Insufficient balance: {user_data['balance']} < {amount}")
            entities["error"] = "Insufficient balance"
            entities["current_balance"] = user_data["balance"]
            state["entities"] = entities
            state["account_number"] = user_data["account_number"]
            state["next_action"] = "generate_response"
        else:
            # Perform transfer
            USERS_DB[user_id]["balance"] -= amount
            USERS_DB[recipient_id]["balance"] += amount
            
            # Record transaction
            if user_id not in TRANSACTIONS_DB:
                TRANSACTIONS_DB[user_id] = []
            if recipient_id not in TRANSACTIONS_DB:
                TRANSACTIONS_DB[recipient_id] = []
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add to sender's transactions
            TRANSACTIONS_DB[user_id].insert(0, {
                "date": timestamp,
                "description": f"Transfer to {recipient_data['name']}",
                "amount": -amount,
                "type": "debit",
                "balance": USERS_DB[user_id]["balance"]
            })
            
            # Add to recipient's transactions
            TRANSACTIONS_DB[recipient_id].insert(0, {
                "date": timestamp,
                "description": f"Transfer from {user_data['name']}",
                "amount": amount,
                "type": "credit",
                "balance": USERS_DB[recipient_id]["balance"]
            })
            
            entities["transfer_successful"] = True
            entities["amount_transferred"] = amount
            entities["recipient_name"] = recipient_data["name"]
            entities["new_balance"] = USERS_DB[user_id]["balance"]
            entities["recipient_account"] = recipient_data["account_number"]
            state["entities"] = entities
            state["account_balance"] = USERS_DB[user_id]["balance"]
            state["account_number"] = user_data["account_number"]
            
            print(f"✅ Transfer successful: ₹{amount:,.2f} from {user_data['name']} to {recipient_data['name']}")
            print(f"   New balance for {user_data['name']}: ₹{USERS_DB[user_id]['balance']:,.2f}")
    else:
        # For general queries, provide basic info
        state["account_number"] = user_data["account_number"]
    
    state["next_action"] = "generate_response"
    state["current_node"] = "banking"
    
    return state


def dialog_manager_agent(state: BankingState) -> BankingState:
    """Dialog Manager Agent: Generates natural responses - Multilingual support"""
    intent = state.get("detected_intent")
    user_text = state.get("transcribed_text")
    user_id = state.get("user_id")
    language = state.get("language", "en")
    
    if not user_id:
        # Respond in user's language
        if language == "hi":
            state["response"] = "कृपया अपनी खाता जानकारी तक पहुंचने के लिए लॉगिन करें।"
        elif language == "gu":
            state["response"] = "કૃપા કરીને તમારી ખાતા માહિતી મેળવવા માટે લૉગિન કરો."
        else:
            state["response"] = "Please log in to access your account information."
        state["next_action"] = "end"
        return state
    
    user_data = USERS_DB[user_id]
    user_name = user_data["name"].split()[0]
    
    # Build detailed context with actual data
    context_parts = []
    if state.get("account_balance") is not None:
        balance = state['account_balance']
        account_num = state.get('account_number', user_data.get('account_number', ''))
        context_parts.append(f"Account Number: {account_num}")
        context_parts.append(f"Current Balance: ₹{balance:,.2f}")
    
    if state.get("transaction_history"):
        transactions = state['transaction_history']
        context_parts.append(f"\nRecent Transactions (showing {len(transactions)} most recent):")
        for i, txn in enumerate(transactions, 1):
            txn_type = txn.get('type', 'unknown').upper()
            amount = txn.get('amount', 0)
            date = txn.get('date', 'N/A')
            desc = txn.get('description', 'N/A')
            context_parts.append(f"{i}. {date} - {txn_type} ₹{amount:,.2f} - {desc}")
    
    if state.get("entities"):
        entities = state['entities']
        if entities.get("loan_balance"):
            context_parts.append(f"\nLoan Balance: ₹{entities['loan_balance']:,.2f}")
        if entities.get("interest_rate"):
            context_parts.append(f"Interest Rate: {entities['interest_rate']}%")
        if entities.get("credit_limit"):
            context_parts.append(f"Credit Limit: ₹{entities['credit_limit']:,.2f}")
    
    if state.get("retrieved_context"):
        context_parts.extend(state["retrieved_context"])
    
    context_str = "\n".join(context_parts)
    
    # Language-specific prompts with STRONG enforcement
    if language == "hi":
        response_prompt = f"""
आप {user_name} से हिंदी में बात कर रहे हैं। 

उपयोगकर्ता का अनुरोध: "{user_text}"
इंटेंट: {intent}

खाता जानकारी:
{context_str}

**बहुत महत्वपूर्ण निर्देश:**
- आपको केवल हिंदी में उत्तर देना है
- अंग्रेजी शब्दों का बिल्कुल उपयोग न करें
- ऊपर दी गई सभी विशिष्ट जानकारी (बैलेंस, ट्रांजेक्शन) को अपने उत्तर में शामिल करें
- 2-3 वाक्यों में संक्षिप्त लेकिन पूर्ण उत्तर दें

अब केवल हिंदी में उत्तर दें:
"""
    elif language == "gu":
        response_prompt = f"""
તમે {user_name} સાથે ગુજરાતીમાં વાત કરો છો.

યુઝરની વિનંતી: "{user_text}"
ઇન્ટેન્ટ: {intent}

ખાતાની માહિતી:
{context_str}

**ખૂબ જ મહત્વપૂર્ણ સૂચનાઓ:**
- તમારે ફક્ત ગુજરાતીમાં જવાબ આપવાનો છે
- અંગ્રેજી શબ્દોનો બિલકુલ ઉપયોગ ન કરો
- ઉપર આપેલી બધી વિગતવાર માહિતી (બેલેન્સ, ટ્રાન્ઝેક્શન) તમારા જવાબમાં સામેલ કરો
- 2-3 વાક્યોમાં સંક્ષિપ્ત પણ સંપૂર્ણ જવાબ આપો

હવે ફક્ત ગુજરાતીમાં જવાબ આપો:
"""
    else:  # English
        response_prompt = f"""
You are speaking to {user_name} in English.

User's request: "{user_text}"
Intent: {intent}

Account Information:
{context_str}

**CRITICAL INSTRUCTIONS:**
- Respond ONLY in English language
- Do NOT use Hindi, Gujarati or any other language
- MUST include ALL specific details from above (balance amounts, transaction details, account numbers)
- For balance queries: State the exact balance amount
- For transaction queries: List the recent transactions with dates, amounts, and descriptions
- Keep the response concise but complete (2-4 sentences)
- Be helpful and professional

Now respond ONLY in English with ALL the specific details:
"""
    
    try:
        # Use SystemMessage + HumanMessage for stronger language enforcement
        if language == "hi":
            messages = [
                SystemMessage(content="आप एक हिंदी बैंकिंग सहायक हैं। आपको हमेशा केवल हिंदी में जवाब देना है।"),
                HumanMessage(content=response_prompt)
            ]
        elif language == "gu":
            messages = [
                SystemMessage(content="તમે એक ગુજરાતી બેન્કિંગ આસિસ્ટન્ટ છો. તમારે હંમેશા ફક્ત ગુજરાતીમાં જ જવાબ આપવાનો છે."),
                HumanMessage(content=response_prompt)
            ]
        else:
            messages = [
                SystemMessage(content="You are an English banking assistant. You must ALWAYS respond ONLY in English and include all specific account details."),
                HumanMessage(content=response_prompt)
            ]
        
        response = llm.invoke(messages)
        generated_response = response.content.strip()
        
        print(f"🤖 LLM Generated Response: {generated_response[:100]}...")
        print(f"🔍 Dialog Manager - Intent: {intent}, Balance in state: {state.get('account_balance')}, User: {user_name}")
        
        # CRITICAL: Always override with actual data for balance, transactions, and loans
        # to prevent LLM hallucination of financial data
        if intent == "check_balance" and state.get("account_balance") is not None:
            balance = state["account_balance"]
            account_num = state.get("account_number", "")
            print(f"✅ Overriding with actual balance: ₹{balance:,.2f}")
            # Always use the actual balance data
            if language == "hi":
                generated_response = f"नमस्ते {user_name}, आपका वर्तमान खाता बैलेंस ₹{balance:,.2f} है। खाता संख्या {account_num}। क्या मैं आपकी और कोई मदद कर सकता हूं?"
            elif language == "gu":
                generated_response = f"નમસ્તે {user_name}, તમારું વર્તમાન ખાતા બેલેન્સ ₹{balance:,.2f} છે. ખાતા નંબર {account_num}. શું હું તમને બીજી કોઈ મદદ કરી શકું?"
            else:
                generated_response = f"Hello {user_name}, your current account balance is ₹{balance:,.2f}. Account number: {account_num}. Is there anything else I can help you with?"
            print(f"✅ Final Response: {generated_response}")
        
        elif intent == "view_transactions" and state.get("transaction_history"):
            transactions = state["transaction_history"]
            print(f"✅ Overriding with {len(transactions)} actual transactions")
            # Always use actual transaction data
            if language == "hi":
                txn_list = "\n".join([f"{i}. {t['date']} - {t['type'].upper()} ₹{t['amount']:,.2f} - {t['description']}" 
                                      for i, t in enumerate(transactions[:3], 1)])
                generated_response = f"नमस्ते {user_name}, यहां आपके हाल के लेनदेन हैं:\n{txn_list}\nक्या आप और विवरण चाहते हैं?"
            elif language == "gu":
                txn_list = "\n".join([f"{i}. {t['date']} - {t['type'].upper()} ₹{t['amount']:,.2f} - {t['description']}" 
                                      for i, t in enumerate(transactions[:3], 1)])
                generated_response = f"નમસ્તે {user_name}, અહીં તમારા તાજેતરના વ્યવહારો છે:\n{txn_list}\nશું તમને વધુ વિગતો જોઈએ છે?"
            else:
                txn_list = "\n".join([f"{i}. {t['date']} - {t['type'].upper()} ₹{t['amount']:,.2f} - {t['description']}" 
                                      for i, t in enumerate(transactions[:3], 1)])
                generated_response = f"Hello {user_name}, here are your recent transactions:\n{txn_list}\nWould you like more details?"
        
        elif intent == "loan_inquiry" and state.get("entities", {}).get("loan_balance"):
            loan_balance = state["entities"]["loan_balance"]
            interest_rate = state["entities"].get("interest_rate", 0)
            # Always use actual loan data
            if language == "hi":
                generated_response = f"नमस्ते {user_name}, आपका लोन बैलेंस ₹{loan_balance:,.2f} है और ब्याज दर {interest_rate}% है। क्या मैं आपकी और कोई मदद कर सकता हूं?"
            elif language == "gu":
                generated_response = f"નમસ્તે {user_name}, તમારું લોન બેલેન્સ ₹{loan_balance:,.2f} છે અને વ્યાજ દર {interest_rate}% છે. શું હું તમને બીજી કોઈ મદદ કરી શકું?"
            else:
                generated_response = f"Hello {user_name}, your loan balance is ₹{loan_balance:,.2f} with an interest rate of {interest_rate}%. Is there anything else I can help you with?"
        
        elif intent == "credit_inquiry" and state.get("entities", {}).get("credit_limit"):
            credit_limit = state["entities"]["credit_limit"]
            # Always use actual credit data
            if language == "hi":
                generated_response = f"नमस्ते {user_name}, आपकी क्रेडिट लिमिट ₹{credit_limit:,.2f} है। क्या मैं आपकी और कोई मदद कर सकता हूं?"
            elif language == "gu":
                generated_response = f"નમસ્તે {user_name}, તમારી ક્રેડિટ લિમિટ ₹{credit_limit:,.2f} છે. શું હું તમને બીજી કોઈ મદદ કરી શકું?"
            else:
                generated_response = f"Hello {user_name}, your credit limit is ₹{credit_limit:,.2f}. Is there anything else I can help you with?"
        
        elif intent == "transfer_funds" and state.get("entities"):
            entities = state["entities"]
            
            # Check for errors
            if entities.get("error"):
                error_msg = entities["error"]
                if error_msg == "Recipient not found":
                    if language == "hi":
                        generated_response = f"क्षमा करें {user_name}, प्राप्तकर्ता नहीं मिला। कृपया सही नाम दोबारा जांचें।"
                    elif language == "gu":
                        generated_response = f"માફ કરશો {user_name}, પ્રાપ્તકર્તા મળ્યો નહીં. કૃપા કરીને સાચું નામ ફરીથી તપાસો."
                    else:
                        generated_response = f"Sorry {user_name}, recipient not found. Please check the recipient name and try again."
                elif error_msg == "Insufficient balance":
                    current_balance = entities.get("current_balance", 0)
                    if language == "hi":
                        generated_response = f"क्षमा करें {user_name}, आपका बैलेंस अपर्याप्त है। वर्तमान बैलेंस: ₹{current_balance:,.2f}।"
                    elif language == "gu":
                        generated_response = f"માફ કરશો {user_name}, તમારું બેલેન્સ અપૂરતું છે. વર્તમાન બેલેન્સ: ₹{current_balance:,.2f}."
                    else:
                        generated_response = f"Sorry {user_name}, insufficient balance. Your current balance is ₹{current_balance:,.2f}."
                else:
                    if language == "hi":
                        generated_response = f"क्षमा करें {user_name}, ट्रांसफर नहीं हो सका। कृपया दोबारा कोशिश करें।"
                    elif language == "gu":
                        generated_response = f"માફ કરશો {user_name}, ટ્રાન્સફર થઈ શક્યું નહીં. કૃપા કરીને ફરી પ્રયાસ કરો."
                    else:
                        generated_response = f"Sorry {user_name}, transfer failed. Please try again."
            
            # Success case
            elif entities.get("transfer_successful"):
                amount = entities["amount_transferred"]
                recipient_name = entities["recipient_name"]
                new_balance = entities["new_balance"]
                recipient_account = entities.get("recipient_account", "")
                
                if language == "hi":
                    generated_response = f"✅ सफल! {user_name}, ₹{amount:,.2f} {recipient_name} को ट्रांसफर कर दिया गया है। आपका नया बैलेंस: ₹{new_balance:,.2f}। प्राप्तकर्ता खाता: {recipient_account}।"
                elif language == "gu":
                    generated_response = f"✅ સફળ! {user_name}, ₹{amount:,.2f} {recipient_name} ને ટ્રાન્સફર કરવામાં આવ્યા છે. તમારું નવું બેલેન્સ: ₹{new_balance:,.2f}. પ્રાપ્તકર્તા ખાતું: {recipient_account}."
                else:
                    generated_response = f"✅ Success! {user_name}, ₹{amount:,.2f} has been transferred to {recipient_name}. Your new balance: ₹{new_balance:,.2f}. Recipient account: {recipient_account}."
                
                print(f"✅ Transfer confirmed: ₹{amount:,.2f} to {recipient_name}, new balance: ₹{new_balance:,.2f}")
        
        state["response"] = generated_response
        
    except Exception as e:
        print(f"⚠️ LLM generation error: {e}")
        # Comprehensive fallback responses based on intent
        if intent == "check_balance" and state.get("account_balance") is not None:
            balance = state["account_balance"]
            account_num = state.get("account_number", "")
            if language == "hi":
                state["response"] = f"नमस्ते {user_name}, आपका वर्तमान खाता बैलेंस ₹{balance:,.2f} है। खाता संख्या {account_num}।"
            elif language == "gu":
                state["response"] = f"નમસ્તે {user_name}, તમારું વર્તમાન ખાતા બેલેન્સ ₹{balance:,.2f} છે. ખાતા નંબર {account_num}."
            else:
                state["response"] = f"Hello {user_name}, your current account balance is ₹{balance:,.2f}. Account number: {account_num}."
        elif intent == "view_transactions" and state.get("transaction_history"):
            transactions = state["transaction_history"][:3]
            if language == "hi":
                txn_list = "\n".join([f"{i}. {t['date']} - {t['type'].upper()} ₹{t['amount']:,.2f} - {t['description']}" 
                                      for i, t in enumerate(transactions, 1)])
                state["response"] = f"नमस्ते {user_name}, यहां आपके हाल के लेनदेन हैं:\n{txn_list}"
            elif language == "gu":
                txn_list = "\n".join([f"{i}. {t['date']} - {t['type'].upper()} ₹{t['amount']:,.2f} - {t['description']}" 
                                      for i, t in enumerate(transactions, 1)])
                state["response"] = f"નમસ્તે {user_name}, અહીં તમારા તાજેતરના વ્યવહારો છે:\n{txn_list}"
            else:
                txn_list = "\n".join([f"{i}. {t['date']} - {t['type'].upper()} ₹{t['amount']:,.2f} - {t['description']}" 
                                      for i, t in enumerate(transactions, 1)])
                state["response"] = f"Hello {user_name}, here are your recent transactions:\n{txn_list}"
        elif intent == "loan_inquiry" and state.get("entities", {}).get("loan_balance"):
            loan_balance = state["entities"]["loan_balance"]
            interest_rate = state["entities"].get("interest_rate", 0)
            if language == "hi":
                state["response"] = f"नमस्ते {user_name}, आपका लोन बैलेंस ₹{loan_balance:,.2f} है और ब्याज दर {interest_rate}% है।"
            elif language == "gu":
                state["response"] = f"નમસ્તે {user_name}, તમારું લોન બેલેન્સ ₹{loan_balance:,.2f} છે અને વ્યાજ દર {interest_rate}% છે."
            else:
                state["response"] = f"Hello {user_name}, your loan balance is ₹{loan_balance:,.2f} with an interest rate of {interest_rate}%."
        elif intent == "credit_inquiry" and state.get("entities", {}).get("credit_limit"):
            credit_limit = state["entities"]["credit_limit"]
            if language == "hi":
                state["response"] = f"नमस्ते {user_name}, आपकी क्रेडिट लिमिट ₹{credit_limit:,.2f} है।"
            elif language == "gu":
                state["response"] = f"નમસ્તે {user_name}, તમારી ક્રેડિટ લિમિટ ₹{credit_limit:,.2f} છે."
            else:
                state["response"] = f"Hello {user_name}, your credit limit is ₹{credit_limit:,.2f}."
        else:
            # Generic fallback
            if language == "hi":
                state["response"] = f"नमस्ते {user_name}, मैं आपकी बैंकिंग जरूरतों में मदद के लिए यहां हूं।"
            elif language == "gu":
                state["response"] = f"નમસ્તે {user_name}, હું તમારી બેન્કિંગ જરૂરિયાતોમાં મદદ કરવા અહીં છું."
            else:
                state["response"] = f"Hello {user_name}, I'm here to help with your banking needs."
    
    state["next_action"] = "end"
    state["current_node"] = "dialog"
    state["compliance_check_passed"] = True
    
    return state


# ============================================================================
# ROUTING
# ============================================================================

def route_next_action(state: BankingState) -> str:
    """Router function to determine next agent"""
    next_action = state.get("next_action", "end")
    
    routing_map = {
        "understand_intent": "intent",
        "retrieve_context": "rag",
        "execute_banking": "banking",
        "generate_response": "dialog",
        "respond": "dialog",
        "end": END
    }
    
    return routing_map.get(next_action, END)


# ============================================================================
# BUILD GRAPH
# ============================================================================

def build_banking_assistant_graph():
    """Build and compile the LangGraph workflow"""
    workflow = StateGraph(BankingState)
    
    # Add nodes
    workflow.add_node("speech", speech_agent)
    workflow.add_node("intent", intent_understanding_agent)
    workflow.add_node("rag", rag_retrieval_agent)
    workflow.add_node("banking", banking_operations_agent)
    workflow.add_node("dialog", dialog_manager_agent)
    
    # Add edges
    workflow.add_edge(START, "speech")
    workflow.add_conditional_edges("speech", route_next_action)
    workflow.add_conditional_edges("intent", route_next_action)
    workflow.add_conditional_edges("rag", route_next_action)
    workflow.add_conditional_edges("banking", route_next_action)
    workflow.add_conditional_edges("dialog", route_next_action)
    
    # Compile with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# Initialize the banking assistant
banking_assistant = build_banking_assistant_graph()

print("✅ Banking Assistant Backend Module Loaded")
