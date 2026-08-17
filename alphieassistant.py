import os
import pytz
import gmail_tool
import gcalendar_tool
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import datetime


load_dotenv()

# Define a list of exit commands that will terminate the chat session
exiting_code = ["quit", "exit", "bye", "goodbye", "stop", "end", "terminate", "close", "shutdown", "abort", "cancel", "finish", "halt", "leave", "log off", "log out", "sign out", "disconnect", "break", "pause", "suspend"]

# Initialize the Gmail service using the get_gmail_service function from gmail_tool
service = gmail_tool.get_gmail_service()

# Initialize the Google Calendar service using the get_calendar_service function from gcalendar_tool
calendar_service = gcalendar_tool.get_calendar_service()

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
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"
    
def check_unread_emails() -> str:
    """Checks for unread emails and returns a summary."""
    if service:
        unread_emails = gmail_tool.get_unread_emails(service)
        return unread_emails
    else:
        return "Gmail service is not available."

def check_upcoming_events() -> str:
    """Gets upcoming events from Google Calendar and returns a summary."""
    if calendar_service:
        upcoming_events = gcalendar_tool.get_upcoming_events(calendar_service)
        return upcoming_events
    else:
        return "Google Calendar service is not available."


# Initialize the GenAI client with the API key from environment
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Create a chat session with the specified model and configuration
chat = client.chats.create(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(
        system_instruction=(
            "Your name is Alphie, a helpful and friendly AI assistant. "
            "Be direct, concise, and useful. Avoid unnecessary repetition and filler words. "
            "You know I'm a Computer Science & Engineering student building you as a long-term project."
            "Always use the tools available to you when appropriate, and if you don't know the answer, say so."
        ),
        tools=[get_current_time, calculation, check_unread_emails, check_upcoming_events]
    )
)


# Print statement to indicate that the assistant is online and ready for interaction
print(f"Assistant online. Type 'quit' to exit.\n")


# Main loop to interact with the user
while True:
    user_input = input("You: ")
    if user_input.lower() in exiting_code:
        print("Exiting the chat. Goodbye!")
        break

    response = chat.send_message(user_input)
    print(f"Alphie: {response.text}")