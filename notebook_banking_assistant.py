"""
Standalone Banking Assistant Module
Extracted from 04_banking_voice_assistant.ipynb
Ready to import into Flask backend
"""

import os
import sys
from typing import Dict, TypedDict, Annotated, List, Optional
import operator
import json
import random
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import httpx

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Walmart authentication (optional)
try:
    from walmart_gpa_peopleai_core.auth_sig import generate_auth_sig
    WALMART_AUTH = True
except ImportError:
    WALMART_AUTH = False

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

print("🔧 Initializing Banking Assistant...")

# Load configuration
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
CONSUMER_ID = os.getenv("CONSUMER_ID")
API_VERSION = os.getenv("API_VERSION", "2024-02-15-preview")
WM_SVC_ENV = os.getenv("WM_SVC_ENV", "prod")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

# Initialize LLM
try:
    if WALMART_AUTH and CONSUMER_ID and PRIVATE_KEY_PATH:
        print("   Using Walmart LLM Gateway authentication...")
        epoch_ts, sig = generate_auth_sig(CONSUMER_ID, PRIVATE_KEY_PATH)
        os.environ["OPENAI_API_KEY"] = CONSUMER_ID
        
        headers = {
            "WM_CONSUMER.ID": CONSUMER_ID,
            "WM_SVC.NAME": "WMTLLMGATEWAY",
            "WM_SVC.ENV": WM_SVC_ENV,
            "WM_SEC.KEY_VERSION": "1",
            "WM_SEC.AUTH_SIGNATURE": sig,
            "WM_CONSUMER.INTIMESTAMP": str(epoch_ts),
            "Content-Type": "application/json",
        }
        
        client = httpx.Client(verify=False, headers=headers)
        async_client = httpx.AsyncClient(verify=False, headers=headers)
        
        llm = AzureChatOpenAI(
            openai_api_key=CONSUMER_ID,
            model=LLM_MODEL,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
            http_client=client,
            http_async_client=async_client,
            temperature=0,
        )
        print("   ✅ LLM initialized with Walmart Gateway")
    else:
        print("   Using standard Azure OpenAI...")
        llm = AzureChatOpenAI(
            model=LLM_MODEL,
            api_version=API_VERSION,
            azure_endpoint=AZURE_ENDPOINT,
            temperature=0,
        )
        print("   ✅ LLM initialized with Azure OpenAI")
except Exception as e:
    print(f"   ⚠️  LLM initialization failed: {e}")
    print("   📝 Will use mock mode")
    llm = None

# ============================================================================
# STATE DEFINITION
# ============================================================================

class BankingState(TypedDict):
    """State schema for banking voice assistant"""
    user_input: str
    transcribed_text: Optional[str]
    messages: Annotated[List[BaseMessage], operator.add]
    conversation_history: List[str]
    is_authenticated: bool
    user_id: Optional[str]
    session_token: Optional[str]
    voice_biometric_verified: bool
    otp_verified: bool
    security_level: str
    detected_intent: Optional[str]
    intent_confidence: float
    entities: Dict[str, any]
    requires_clarification: bool
    clarification_question: Optional[str]
    account_number: Optional[str]
    account_balance: Optional[float]
    transaction_history: List[Dict]
    pending_transaction: Optional[Dict]
    retrieved_context: List[str]
    knowledge_base_results: List[Dict]
    response: str
    tts_audio: Optional[str]
    next_action: str
    current_node: str
    error: Optional[str]
    compliance_check_passed: bool

# ============================================================================
# MOCK DATA
# ============================================================================

USERS_DB = {
    "user_001": {
        "name": "John Doe",
        "account_number": "ACC123456789",
        "balance": 15750.50,
        "voice_signature": "verified",
        "phone": "+1234567890",
        "credit_limit": 50000.00,
        "loan_balance": 120000.00,
        "interest_rate": 3.5
    }
}

TRANSACTIONS_DB = {
    "user_001": [
        {"date": "2025-11-20", "type": "debit", "amount": 150.00, "description": "Grocery Store", "balance": 15750.50},
        {"date": "2025-11-18", "type": "credit", "amount": 3000.00, "description": "Salary Deposit", "balance": 15900.50},
        {"date": "2025-11-15", "type": "debit", "amount": 85.25, "description": "Restaurant", "balance": 12900.50},
    ]
}

KNOWLEDGE_BASE = [
    {"topic": "interest_rates", "content": "Current savings account interest rate is 2.5% per annum. Home loan rates start at 7.25% with flexible repayment options."},
    {"topic": "credit_cards", "content": "Credit cards with 0% introductory interest for 12 months, rewards programs, cashback benefits, no annual fees for the first year."},
    {"topic": "transfer_limits", "content": "Daily NEFT/RTGS transfer limit is ₹5,00,000 for verified accounts. IMPS transfers have a limit of ₹2,00,000."},
]

# ============================================================================
# AGENT NODES
# ============================================================================

def speech_agent(state: BankingState) -> BankingState:
    """Speech Agent: Process user input"""
    if state.get("user_input"):
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
            "next_action": "understand_intent"
        }
    return {**state, "error": "No input", "next_action": "end"}


def intent_understanding_agent(state: BankingState) -> BankingState:
    """Intent Agent: Detect user intent"""
    user_text = state.get("transcribed_text", "")
    
    if not llm:
        # Fallback intent detection
        intents = {
            "balance": "check_balance",
            "transaction": "view_transactions",
            "transfer": "transfer_funds",
            "loan": "loan_inquiry",
            "credit": "credit_inquiry"
        }
        detected = "general_question"
        for keyword, intent in intents.items():
            if keyword in user_text.lower():
                detected = intent
                break
        
        return {
            **state,
            "detected_intent": detected,
            "intent_confidence": 0.85,
            "entities": {},
            "next_action": "retrieve_context"
        }
    
    # Use LLM for intent detection
    try:
        intent_prompt = f"""Analyze: "{user_text}"
Return JSON: {{"intent": "<check_balance|view_transactions|transfer_funds|loan_inquiry|credit_inquiry|general_question>", "confidence": <float>, "entities": {{}}}}"""
        
        response = llm.invoke(intent_prompt)
        result = json.loads(response.content)
        
        return {
            **state,
            "detected_intent": result["intent"],
            "intent_confidence": result["confidence"],
            "entities": result.get("entities", {}),
            "next_action": "retrieve_context"
        }
    except:
        return {**state, "detected_intent": "general_question", "next_action": "retrieve_context"}


def rag_retrieval_agent(state: BankingState) -> BankingState:
    """RAG Agent: Retrieve relevant context"""
    intent = state.get("detected_intent", "")
    
    topic_map = {
        "loan_inquiry": ["interest_rates"],
        "credit_inquiry": ["credit_cards"],
        "transfer_funds": ["transfer_limits"],
    }
    
    topics = topic_map.get(intent, [])
    docs = [doc["content"] for doc in KNOWLEDGE_BASE if doc["topic"] in topics]
    
    return {**state, "retrieved_context": docs, "next_action": "execute_banking"}


def banking_operations_agent(state: BankingState) -> BankingState:
    """Banking Ops Agent: Execute operations"""
    intent = state.get("detected_intent")
    user_id = state.get("user_id", "user_001")
    
    user_data = USERS_DB.get(user_id, USERS_DB["user_001"])
    
    if intent == "check_balance":
        state["account_balance"] = user_data["balance"]
    elif intent == "view_transactions":
        state["transaction_history"] = TRANSACTIONS_DB.get(user_id, [])[:5]
    elif intent == "loan_inquiry":
        state["entities"]["loan_balance"] = user_data.get("loan_balance", 0)
        state["entities"]["interest_rate"] = user_data.get("interest_rate", 0)
    elif intent == "credit_inquiry":
        state["entities"]["credit_limit"] = user_data.get("credit_limit", 0)
    
    state["account_number"] = user_data["account_number"]
    state["next_action"] = "generate_response"
    return state


def dialog_manager_agent(state: BankingState) -> BankingState:
    """Dialog Manager: Generate response"""
    intent = state.get("detected_intent")
    user_text = state.get("transcribed_text")
    user_id = state.get("user_id", "user_001")
    user_data = USERS_DB.get(user_id, USERS_DB["user_001"])
    user_name = user_data["name"].split()[0]
    
    # Build context
    context_parts = []
    if state.get("account_balance"):
        context_parts.append(f"Balance: ₹{state['account_balance']:,.2f}")
    if state.get("transaction_history"):
        context_parts.append(f"Transactions: {len(state['transaction_history'])}")
    if state.get("retrieved_context"):
        context_parts.extend(state["retrieved_context"])
    
    context_str = "\n".join(context_parts)
    
    if not llm:
        # Fallback responses
        responses = {
            "check_balance": f"Hello {user_name}, your account balance is ₹{state.get('account_balance', 15750.50):,.2f}. How else can I help?",
            "view_transactions": f"{user_name}, here are your recent transactions. You had {len(state.get('transaction_history', []))} transactions this week.",
            "loan_inquiry": f"Your home loan balance is ₹{state['entities'].get('loan_balance', 120000):,.2f} at {state['entities'].get('interest_rate', 7.5)}% per annum.",
            "credit_inquiry": f"Your credit limit is ₹{state['entities'].get('credit_limit', 50000):,.2f}.",
        }
        response_text = responses.get(intent, f"Hello {user_name}, how can I help you with your banking today?")
    else:
        # Use LLM for response
        try:
            prompt = f"""You are an SBI assistant speaking to {user_name}.

Request: "{user_text}"
Intent: {intent}

Context:
{context_str}

Generate a helpful 2-3 sentence response."""
            
            response = llm.invoke(prompt)
            response_text = response.content.strip()
        except:
            response_text = f"Hello {user_name}, I'm here to help with your banking needs."
    
    state["response"] = response_text
    state["next_action"] = "end"
    state["compliance_check_passed"] = True
    return state


# ============================================================================
# ROUTING
# ============================================================================

def route_next_action(state: BankingState) -> str:
    """Route to next agent"""
    routing = {
        "understand_intent": "intent",
        "retrieve_context": "rag",
        "execute_banking": "banking",
        "generate_response": "dialog",
        "end": END
    }
    return routing.get(state.get("next_action", "end"), END)


# ============================================================================
# BUILD GRAPH
# ============================================================================

def build_banking_assistant():
    """Build LangGraph workflow"""
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
    
    # Compile
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# Initialize
banking_assistant = build_banking_assistant()
print("✅ Banking Assistant Ready!")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Banking Assistant...")
    print("="*60)
    
    test_state = {
        "user_input": "What's my account balance?",
        "transcribed_text": None,
        "messages": [],
        "conversation_history": [],
        "is_authenticated": True,
        "user_id": "user_001",
        "session_token": "test_token",
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
        "compliance_check_passed": False
    }
    
    result = banking_assistant.invoke(test_state, {"configurable": {"thread_id": "test"}})
    print(f"\n✅ Response: {result.get('response')}")
    print("="*60)
