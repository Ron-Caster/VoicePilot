import os
import json
import webbrowser
import threading

try:
    from langchain.chat_models import init_chat_model # This actually remains valid, but often comes from langchain-community or specific providers
    from langchain_core.messages import SystemMessage, HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# System prompt for the model
system_prompt = (
    "You are a parser that converts user requests to open websites or mail services "
    "into a strict JSON command. Only output JSON of the form:\n"
    "{ \"action\": \"open_url\", \"url\": \"<FULL_URL>\" }\n"
    "No additional text or explanation."
)

# Initialize model only once
model = None
if LANGCHAIN_AVAILABLE and "GROQ_API_KEY" in os.environ:
    try:
        model = init_chat_model("llama-3.1-8b-instant", model_provider="groq")
    except Exception as e:
        print(f"⚠️ Model initialization failed: {str(e)}")

def get_url_from_command(user_query: str) -> str:
    """Convert natural language command to URL using LLM"""
    if not model:
        if not LANGCHAIN_AVAILABLE:
            print("🔴 LangChain not installed. Run: pip install langchain-core langchain-groq")
        elif "GROQ_API_KEY" not in os.environ:
            print("🔴 GROQ_API_KEY environment variable not set")
        return ""
    
    messages = [SystemMessage(content=system_prompt), 
                HumanMessage(content=user_query)]
    try:
        ai_reply = model.invoke(messages)
        cmd = json.loads(ai_reply.content.strip())
        return cmd["url"] if cmd.get("action") == "open_url" else ""
    except Exception as e:
        print(f"🔴 Processing error: {str(e)}")
        return ""

def open_website(command: str):
    """Handle website opening in a background thread"""
    print(f"🌐 Processing: {command}")
    
    # First try direct URL pattern
    if "." in command and " " not in command:
        url = f"https://{command}" if not command.startswith(("http://", "https://")) else command
        webbrowser.open(url)
        print(f"✅ Opened: {url}")
        return
    
    # Use LLM for complex requests
    url = get_url_from_command(command)
    if url:
        webbrowser.open(url)
        print(f"✅ Opened: {url}")
    else:
        print(f"❌ Couldn't find URL for: {command}")

def open_website_threaded(command: str):
    """Threaded wrapper for website opening"""
    threading.Thread(target=open_website, args=(command,), daemon=True).start()