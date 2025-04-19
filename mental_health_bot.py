import streamlit as st
import requests
import json
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os
import time
from datetime import datetime

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def get_chat_response(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Mental Health Chatbot"
    }
    
    # Format messages for the API
    formatted_messages = []
    for msg in messages:
        if msg["role"] == "system":
            formatted_messages.append({"role": "system", "content": msg["content"]})
        elif msg["role"] == "user":
            formatted_messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            formatted_messages.append({"role": "assistant", "content": msg["content"]})
    
    data = {
        "model": "anthropic/claude-2",
        "messages": formatted_messages,
        "temperature": 0.7,
        "max_tokens": 500,  # Reduced token limit
        "stream": False
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        # Debug print to check response format
        print("API Response:", response_data)
        
        # Check for credit limit error
        if "error" in response_data:
            error_msg = response_data["error"].get("message", "Unknown error")
            if "credits" in error_msg.lower():
                st.error("API Error: Insufficient credits. Please upgrade your account at https://openrouter.ai/settings/credits")
                return None
            else:
                st.error(f"API Error: {error_msg}")
                return None
        
        if not isinstance(response_data, dict):
            st.error("Invalid response format: Response is not a dictionary")
            return None
            
        if "choices" not in response_data:
            st.error("Invalid response format: Missing 'choices' field")
            return None
            
        if not isinstance(response_data["choices"], list):
            st.error("Invalid response format: 'choices' is not a list")
            return None
            
        if len(response_data["choices"]) == 0:
            st.error("No choices in response")
            return None
            
        choice = response_data["choices"][0]
        if "message" not in choice:
            st.error("Invalid response format: Missing 'message' field in choice")
            return None
            
        if "content" not in choice["message"]:
            st.error("Invalid response format: Missing 'content' field in message")
            return None
            
        return response_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error making API request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error parsing API response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# Set page configuration with custom theme
st.set_page_config(
    page_title="Mental Health Support Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI with multi-color theme
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    
    /* Chat container styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        max-width: 80%;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* User message styling */
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, #4a00e0 0%, #8e2de2 100%);
        border-left: 4px solid #ff6b6b;
        color: #ffffff;
        margin-left: auto;
        margin-right: 0;
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="assistant"] {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        border-left: 4px solid #ffd93d;
        color: #ffffff;
        margin-left: 0;
        margin-right: auto;
    }
    
    /* Input container */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        z-index: 1000;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Input box styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 25px;
        padding: 12px 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
        outline: none;
    }
    
    /* Input placeholder styling */
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
        color: white;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff8e8e 0%, #ff6b6b 100%);
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
        padding: 2rem 1rem;
    }
    
    /* Title styling */
    h1 {
        color: #ffffff;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: none;
        -webkit-background-clip: none;
        -webkit-text-fill-color: #ffffff;
    }
    
    /* Subtitle styling */
    h2 {
        color: #ffd93d;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    
    /* Chat area container */
    .chat-area {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        margin-bottom: 80px;
    }
    
    /* Markdown text color */
    .stMarkdown {
        color: #ffffff;
    }
    
    /* Streamlit default text color */
    .stText {
        color: #ffffff;
    }
    
    /* Streamlit app container */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        min-height: 100vh;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ffd93d 0%, #ff6b6b 100%);
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #ff6b6b;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Mood selector styling */
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        color: #ffffff;
    }
    
    /* Timestamp styling */
    .stCaption {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    
    /* Breathing exercise styling */
    .breathing-container {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        margin: 1rem 0;
    }

    .breathing-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
        margin: 20px auto;
        animation: breathe 4s infinite ease-in-out;
    }

    @keyframes breathe {
        0% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.2);
            opacity: 1;
        }
        100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
    }

    .breathing-text {
        text-align: center;
        color: #ffffff;
        font-size: 1.2rem;
        margin-top: 10px;
        animation: pulse 2s infinite;
    }

    .breathing-instructions {
        color: #ffffff;
        font-size: 1rem;
        margin: 10px 0;
        line-height: 1.5;
    }

    .breathing-count {
        font-size: 2rem;
        color: #ff6b6b;
        margin: 10px 0;
        font-weight: bold;
    }

    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }

    .breathing-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 10px 0;
    }

    .breathing-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Block container */
    .block-container {
        padding-bottom: 100px !important;
    }

    /* Element container */
    .element-container {
        margin-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.mood = "neutral"
    st.session_state.first_run = True
    
    # Add system message
    system_message = {
        "role": "system",
        "content": """You are Imtiaz, a compassionate and supportive mental health chatbot. 
        Your role is to provide emotional support, active listening, and general guidance while being mindful of these important guidelines:
        
        1. Always maintain a warm, empathetic, and non-judgmental tone
        2. Never provide medical advice or attempt to diagnose conditions
        3. Encourage professional help when appropriate
        4. Focus on active listening and emotional support
        5. Use validation and reflection techniques
        6. Maintain appropriate boundaries
        7. Be clear about being an AI assistant
        8. Prioritize user safety and well-being
        
        If someone expresses thoughts of self-harm or suicide, immediately provide crisis hotline information and encourage seeking professional help."""
    }
    st.session_state.messages = [system_message]

# Sidebar content
with st.sidebar:
    st.title("🧠 About")
    st.markdown("""
    ### Welcome to Mental Health Support Chat
    
    This AI-powered chatbot is here to provide emotional support and a listening ear. 
    While not a replacement for professional care, it offers a safe space to express yourself.
    
    ### How to Use
    1. Type your thoughts or feelings in the chat
    2. The AI will respond with empathy and support
    3. Feel free to share as much or as little as you're comfortable with
    
    ### Important Note
    This is an AI assistant, not a licensed mental health professional.
    """)
    
    # Mood selector
    st.markdown("---")
    st.subheader("How are you feeling today?")
    mood = st.select_slider(
        "Select your mood",
        options=["😢 Sad", "😔 Low", "😐 Neutral", "🙂 Good", "😊 Happy"],
        value="😐 Neutral"
    )
    st.session_state.mood = mood
    
    # Resources section
    st.markdown("---")
    st.subheader("Crisis Resources")
    st.markdown("""
    ### Emergency Numbers
    - *Bangladesh Emergency*: 999
    - *BD Crisis Hotline*: 999

    
    ### International Support
    - [International Crisis Resources](https://www.iasp.info/resources/Crisis_Centres/)
    - [Find Local Support](https://www.iasp.info/resources/Crisis_Centres/)
    """)
    
    # Breathing exercise
    st.markdown("---")
    st.subheader("Quick Breathing Exercise")
    if st.button("Start Breathing Exercise"):
        with st.spinner("Follow the circle..."):
            st.markdown("""
            <div style='text-align: center;'>
                <div class='breathing-circle'></div>
                <p class='breathing-text'>Breathe in... and out...</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(8)  # Increased duration for better breathing exercise

# Main content
st.title("Mental Health Support Chat")
st.markdown("""
<div style='background: linear-gradient(135deg, #4a00e0 0%, #8e2de2 100%); padding: 1rem; border-radius: 15px; margin-bottom: 1rem;'>
    <p style='color: #ffffff; margin: 0;'>
        💬 I'm here to listen and provide emotional support. Feel free to share what's on your mind.
    </p>
</div>
""", unsafe_allow_html=True)

# Chat area
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

# Display welcome message if first run
if st.session_state.first_run:
    with st.chat_message("assistant"):
        st.markdown("""
        <div class="message-content">
            Hi! 👋 I'm Imtiaz, your mental health support assistant. I'm here to:
            
            - Listen to your thoughts and feelings
            - Provide emotional support
            - Help you process your emotions
            - Offer gentle guidance when needed
            
            How are you feeling today? You can select your mood in the sidebar and share what's on your mind.
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Started at {datetime.now().strftime('%H:%M')}")
    st.session_state.first_run = False

# Chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"""
            <div class="message-content">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Sent at {datetime.now().strftime('%H:%M')}")
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f"""
            <div class="message-content">
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Responded at {datetime.now().strftime('%H:%M')}")
    elif message["role"] == "system":
        continue

st.markdown('</div>', unsafe_allow_html=True)

# Input container
st.markdown('<div class="input-container">', unsafe_allow_html=True)
user_input = st.text_input(
    "Share what's on your mind...",
    key="chat_input",
    placeholder=f"I'm feeling {st.session_state.mood.split()[1].lower()} today..."
)
st.markdown('</div>', unsafe_allow_html=True)

if user_input:
    try:
        # Add user message to state and display
        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.markdown(f"""
            <div class="message-content">
                {user_input}
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Sent at {datetime.now().strftime('%H:%M')}")

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get response from the model
                    response = get_chat_response(st.session_state.messages)
                    
                    if response is None:
                        st.error("Unable to connect to the API. Please check your internet connection.")
                    elif "choices" not in response:
                        st.error("Invalid response format from the API.")
                    elif len(response["choices"]) == 0:
                        st.error("No response generated. Please try again.")
                    else:
                        response_content = response["choices"][0]["message"]["content"]
                        if not response_content:
                            st.error("Empty response received. Please try again.")
                        else:
                            st.markdown(f"""
                            <div class="message-content">
                                {response_content}
                            </div>
                            """, unsafe_allow_html=True)
                            st.caption(f"Responded at {datetime.now().strftime('%H:%M')}")
                            
                            # Add assistant response to messages
                            assistant_message = {
                                "role": "assistant",
                                "content": response_content
                            }
                            st.session_state.messages.append(assistant_message)
                
                except Exception as e:
                    st.error(f"Error getting response: {str(e)}")
                    st.info("Please try again or refresh the page.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try again or refresh the page.")

# Footer
st.markdown("""
    <div class="footer">
        <p style='text-align: center; color: #ffffff;'>
            Remember: If you're experiencing a mental health emergency, please contact emergency services 
            or reach out to a mental health professional immediately.
        </p>
    </div>
    """, unsafe_allow_html=True)