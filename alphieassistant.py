import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import datetime
import pytz

load_dotenv()

# Define a list of exit commands that will terminate the chat session
exiting_code = ["quit", "exit", "bye", "goodbye", "stop", "end", "terminate", "close", "shutdown", "abort", "cancel", "finish", "halt", "leave", "log off", "log out", "sign out", "disconnect", "break", "pause", "suspend"]

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
        tools=[get_current_time, calculation]
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