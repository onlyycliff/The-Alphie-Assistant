import ast
import json
import logging
import operator
import os
from datetime import datetime

import pytz
from dotenv import load_dotenv
from google import genai
from google.genai import types

import audio_recording
import gcalendar_tool
import gmail_tool
import whisper_tool

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Define a list of exit commands that will terminate the chat session
exiting_code = ["quit", "exit", "bye", "goodbye", "stop", "end", "terminate", "close", "shutdown", "abort", "cancel", "finish", "halt", "leave", "log off", "log out", "sign out", "disconnect", "break", "pause", "suspend"]

USE_SEARCH_GROUNDING = os.getenv("USE_SEARCH_GROUNDING", "False") == "True"
# "gemini" (default) or "groq" -- groq serves free, open-weight models (e.g.
# openai/gpt-oss-120b) with an OpenAI-compatible tool-calling API.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Services/models are loaded lazily on first use, not at import time, so a
# text-only session doesn't pay Gmail/Calendar OAuth or Whisper model-load cost.
_gmail_service = None
_calendar_service = None
_whisper_model = None
_whisper_model_loaded = False


def get_gmail_service_cached():
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = gmail_tool.get_gmail_service()
    return _gmail_service


def get_calendar_service_cached():
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = gcalendar_tool.get_calendar_service()
    return _calendar_service


def get_whisper_model_cached():
    global _whisper_model, _whisper_model_loaded
    if not _whisper_model_loaded:
        _whisper_model = whisper_tool.get_model()
        _whisper_model_loaded = True
    return _whisper_model


# Restricted arithmetic evaluator used by calculation() instead of eval().
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_safe_eval_node(node.left), _safe_eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        return _SAFE_OPERATORS[type(node.op)](_safe_eval_node(node.operand))
    raise ValueError("unsupported expression")


# Function to get the current time in a specified timezone
def get_current_time(timezone: str = "America/New_York") -> str:
    """Returns the current time in the specified timezone."""
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Function that evaluates a mathematical expression
def calculation(expression: str) -> str:
    """Evaluates a mathematical expression and returns the result."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

def check_unread_emails() -> str:
    """Checks for unread emails and returns a summary."""
    service = get_gmail_service_cached()
    if service:
        return gmail_tool.get_unread_emails(service)
    return "Gmail service is not available."

def check_upcoming_events() -> str:
    """Gets upcoming events from Google Calendar and returns a summary."""
    service = get_calendar_service_cached()
    if service:
        return gcalendar_tool.get_upcoming_events(service)
    return "Google Calendar service is not available."


TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculation": calculation,
    "check_unread_emails": check_unread_emails,
    "check_upcoming_events": check_upcoming_events,
}

# JSON-schema tool descriptions for the Groq (OpenAI-compatible) path. Gemini
# instead introspects the plain functions directly, so it doesn't need these.
GROQ_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns the current time in the specified timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "IANA timezone name, e.g. America/New_York"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculation",
            "description": "Evaluates a mathematical expression and returns the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "A math expression, e.g. 2 + 2 * 3"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_unread_emails",
            "description": "Checks for unread emails and returns a summary.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_upcoming_events",
            "description": "Gets upcoming events from Google Calendar and returns a summary.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

SYSTEM_INSTRUCTION = (
    "Your name is Alphie, a helpful and friendly AI assistant. "
    "Be direct, concise, and useful. Avoid unnecessary repetition and filler words. "
    "You know I'm a Computer Science & Engineering student building you as a long-term project. "
    "Always use the tools available to you when appropriate, and if you don't know the answer, say so."
)


def build_gemini_chat():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    tools = [get_current_time, calculation, check_unread_emails, check_upcoming_events]
    if USE_SEARCH_GROUNDING:
        tools.append(types.Tool(google_search=types.GoogleSearch()))
    return client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, tools=tools),
    )


def send_gemini_message(chat, user_input: str) -> str:
    response = chat.send_message(user_input)
    return response.text


def build_groq_client():
    from groq import Groq
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_groq_turn(client, history: list, user_input: str) -> str:
    """Sends a message to Groq and manually drives the tool-call loop
    (Groq's OpenAI-compatible API returns tool_calls for the caller to
    execute and feed back, unlike Gemini's automatic function calling)."""
    history.append({"role": "user", "content": user_input})
    while True:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=history,
            tools=GROQ_TOOL_SCHEMAS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        if message.tool_calls:
            history.append(message)
            for tool_call in message.tool_calls:
                func = TOOL_FUNCTIONS.get(tool_call.function.name)
                if func is None:
                    result = f"Unknown tool: {tool_call.function.name}"
                else:
                    args = json.loads(tool_call.function.arguments or "{}")
                    try:
                        result = func(**args)
                    except Exception as e:
                        result = f"Error running tool {tool_call.function.name}: {e}"
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })
            continue
        history.append({"role": "assistant", "content": message.content})
        return message.content


def main():
    if LLM_PROVIDER == "groq":
        client = build_groq_client()
        history = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

        def send(text):
            return run_groq_turn(client, history, text)
    else:
        chat = build_gemini_chat()

        def send(text):
            return send_gemini_message(chat, text)

    print("Assistant online. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip() == "" or user_input.lower() == "v":
            recorded_file = audio_recording.listen_and_record()
            transcription = whisper_tool.transcribe_audio(get_whisper_model_cached(), recorded_file)
            if transcription is None:
                print("Alphie: Sorry, voice input isn't available right now.")
                continue
            user_input = transcription
            print(f"You (voice): {user_input}")

        if user_input.lower() in exiting_code:
            print("Exiting the chat. Goodbye!")
            break

        reply = send(user_input)
        print(f"Alphie: {reply}")


if __name__ == "__main__":
    main()
