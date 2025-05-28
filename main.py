import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import time

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Load environment variables
load_dotenv()

# Initialize Groq client
try:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found in environment variables")
        st.info("Please set your GROQ_API_KEY in the .env file")
        st.stop()
    
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.stop()

# Available models with enhanced descriptions and configurations
AVAILABLE_MODELS = {
    "llama-3.3-70b-versatile": {
        "description": "Most capable model for general tasks",
        "max_tokens": 4096,
        "category": "General"
    },
    "codellama-70b-instruct": {
        "description": "Specialized for code generation and programming tasks",
        "max_tokens": 4096,
        "category": "Code",
        "system_prompt": "You are an expert programmer. Provide clear, efficient, and well-documented code solutions."
    },
    "mixtral-8x7b-32768": {
        "description": "Advanced model for mathematical reasoning and calculations",
        "max_tokens": 32768,
        "category": "Mathematics",
        "system_prompt": "You are a mathematical expert. Provide detailed step-by-step solutions and explanations."
    },
    "llama-3.3-70b-instruct": {
        "description": "Specialized for mathematical problem-solving and analysis",
        "max_tokens": 4096,
        "category": "Mathematics",
        "system_prompt": "You are a mathematical expert. Focus on precise calculations and logical reasoning."
    },
    "python-expert": {
        "description": "Specialized Python code generation and optimization",
        "max_tokens": 4096,
        "category": "Python",
        "system_prompt": """You are an expert Python developer. Follow these guidelines:
1. Write clean, PEP 8 compliant Python code
2. Include type hints and docstrings
3. Add comments explaining complex logic
4. Use modern Python features (3.8+)
5. Include error handling and input validation
6. Provide usage examples
7. Consider performance and best practices
8. Use appropriate design patterns when needed"""
    }
}

# Set page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
    }
    .error-message {
        background-color: #ff6b6b;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .model-category {
        font-size: 0.8em;
        color: #666;
        margin-top: 0.2rem;
    }
    .code-block {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Consolas', monospace;
        margin: 1rem 0;
        white-space: pre-wrap;
    }
    .math-block {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Times New Roman', serif;
        margin: 1rem 0;
    }
    .python-keyword {
        color: #569CD6;
    }
    .python-string {
        color: #CE9178;
    }
    .python-comment {
        color: #6A9955;
    }
    .python-function {
        color: #DCDCAA;
    }
    </style>
    """, unsafe_allow_html=True)

# Callback functions
def clear_chat():
    st.session_state.messages = []
    st.session_state.processing = False

def process_input():
    if st.session_state.user_input and not st.session_state.processing:
        st.session_state.processing = True
        
        try:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": st.session_state.user_input})
            
            # Get selected model configuration
            model_config = AVAILABLE_MODELS[st.session_state.selected_model]
            
            # Prepare system message if available
            messages = []
            if "system_prompt" in model_config:
                messages.append({"role": "system", "content": model_config["system_prompt"]})
            
            # Add conversation history
            messages.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
            
            # Show loading animation
            with st.spinner("Thinking..."):
                max_retries = 3
                retry_delay = 2  # seconds
                
                for attempt in range(max_retries):
                    try:
                        # Get AI response
                        chat_completion = client.chat.completions.create(
                            messages=messages,
                            model=st.session_state.selected_model,
                            temperature=0.7,
                            max_tokens=model_config["max_tokens"]
                        )
                        
                        # Add assistant response to chat history
                        assistant_response = chat_completion.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        if "429" in str(e) and attempt < max_retries - 1:
                            # Rate limit hit, wait and retry
                            time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                            continue
                        else:
                            # Other error or max retries reached
                            raise e
                
        except Exception as e:
            error_message = f"""
                <div class="error-message">
                    <strong>Error:</strong> {str(e)}<br>
                    Please try again in a few moments.
                </div>
            """
            st.markdown(error_message, unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I apologize, but I encountered an error. Please try again in a few moments."
            })
        
        finally:
            st.session_state.processing = False
            st.session_state.user_input = ""

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model selection with categories
    st.subheader("Select Model")
    
    # Group models by category
    model_categories = {}
    for model_name, model_info in AVAILABLE_MODELS.items():
        category = model_info["category"]
        if category not in model_categories:
            model_categories[category] = []
        model_categories[category].append(model_name)
    
    # Create selectbox with grouped options
    selected_model = st.selectbox(
        "Choose a model",
        options=list(AVAILABLE_MODELS.keys()),
        format_func=lambda x: f"{x} - {AVAILABLE_MODELS[x]['description']}",
        help="Select a model based on your needs"
    )
    st.session_state.selected_model = selected_model
    
    # Display model details
    st.markdown("---")
    st.subheader("Model Details")
    model_info = AVAILABLE_MODELS[selected_model]
    st.markdown(f"**Category:** {model_info['category']}")
    st.markdown(f"**Max Tokens:** {model_info['max_tokens']}")
    if "system_prompt" in model_info:
        st.markdown(f"**Specialization:** {model_info['system_prompt']}")
    
    # Clear chat button
    if st.button("Clear Chat", type="secondary", on_click=clear_chat):
        pass

# Main chat interface
st.title("🤖 AI Assistant")
st.markdown("---")

# Display chat history with enhanced formatting
for message in st.session_state.messages:
    with st.container():
        # Determine if the message contains code or math
        content = message['content']
        if "```python" in content:
            # Format Python code blocks with syntax highlighting
            content = content.replace("```python", "<div class='code-block'>")
            content = content.replace("```", "</div>")
        elif "```" in content:
            # Format other code blocks
            content = content.replace("```", "<div class='code-block'>")
            content = content.replace("```", "</div>")
        elif any(math_symbol in content for math_symbol in ["∫", "∑", "∏", "√", "∞", "≠", "≤", "≥"]):
            # Format math blocks
            content = f"<div class='math-block'>{content}</div>"
        
        st.markdown(f"""
            <div class="chat-message {message['role']}">
                <strong>{message['role'].title()}:</strong><br>
                {content}
            </div>
        """, unsafe_allow_html=True)

# Chat input with Python-specific help
st.text_area(
    "Type your message here...",
    key="user_input",
    height=100,
    on_change=process_input,
    help="""For Python code generation:
1. Select the 'python-expert' model
2. Describe what you want to create
3. Specify any requirements or constraints
4. Mention if you need specific libraries or features

Example: 'Create a Python function that processes CSV files using pandas and includes error handling'"""
)