import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = client.chats.create(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(
        system_instruction=(
            "Your name is Alphie, a helpful and friendly AI assistant. "
            "Be direct, concise, and useful. Avoid unnecessary repetition and filler words. "
            "You know I'm a Computer Science & Engineering student building you as a long-term project."
        )
    )
)


print(f"Assistant online. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print("Exiting the chat. Goodbye!")
        break

    response = chat.send_message(user_input)
    print(f"Alphie: {response.text}")