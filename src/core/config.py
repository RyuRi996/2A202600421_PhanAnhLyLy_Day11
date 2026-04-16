"""
Lab 11 — Configuration & API Key Setup
"""
import os
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Inject OpenAI Proxy transparently
from . import openai_proxy
openai_proxy.patch_genai_for_openai()

def setup_api_key():
    """Load API key from environment or prompt."""
    if load_dotenv:
        # override=True ensures .env takes precedence over existing terminal variables
        load_dotenv(override=True)
        
    # Fake Google API key so ADK doesn't crash during initialization
    os.environ["GOOGLE_API_KEY"] = "mock_key_for_proxy"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
    
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = input("Enter OpenAI API Key: ")
    
    # Kiểm tra biến OpenAI API
    api_key = os.environ.get("OPENAI_API_KEY", "")
    masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 15 else "invalid_key"
    print(f"OpenAI API key loaded (Active key: {masked_key})")


# Allowed banking topics (used by topic_filter)
ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
]

# Blocked topics (immediate reject)
BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
