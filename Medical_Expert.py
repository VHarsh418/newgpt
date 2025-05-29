import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

query = input("Enter your question: ")
prompt = (
    f"You are a medical expert. Your task is to answer only health or medicine-related questions. "
    f"If the user asks anything outside of healthcare, simply reply with 'I don't know.' "
    f"The user's query is: {query}"
)



chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": query,
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)