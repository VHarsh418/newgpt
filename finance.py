import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in your .env file.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Get user input
query = input("Enter your question: ")

# Create prompt
prompt = (
    f"You are a financial expert. Your task is to answer only finance-related questions. "
    f"If the user asks anything outside of finance, simply reply with 'I don't know.' "
    f"The user's query is: {query}"
)

# Get response from Groq
try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {str(e)}")