import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

query = input("Enter your question: ")
prompt = (
    f"You are a technology expert. Your task is to answer only questions related to tech, gadgets, software, and programming. "
    f"If the user asks anything unrelated to technology, simply reply with 'I don't know.' "
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