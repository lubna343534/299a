# Mental Health Support Chatbot

A compassionate AI-powered mental health support chatbot built with LangChain, OpenRouter, and Streamlit. This chatbot provides emotional support and a listening ear while maintaining appropriate boundaries and encouraging professional help when needed.

## Features

- 🤝 Empathetic and supportive conversations
- 🔒 Safe and private environment
- 🎯 Focus on emotional support and active listening
- ⚡ Real-time responses
- 🚨 Crisis resources readily available

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone this repository or download the files

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Chatbot

To start the chatbot, run:
```bash
streamlit run mental_health_bot.py
```

The application will open in your default web browser at `http://localhost:8501`

## Important Notes

- This chatbot is NOT a replacement for professional mental health care
- In case of emergency, please contact your local emergency services or crisis hotline
- The chatbot maintains appropriate boundaries and will encourage professional help when needed

## Crisis Resources

- National Crisis Hotline (US): 988
- Crisis Text Line: Text HOME to 741741

## Technical Details

The chatbot uses:
- LangChain for chat functionality
- OpenRouter API for language model access
- Streamlit for the user interface
- Claude 2 model via OpenRouter for generating responses

## Security

The application uses environment variables for API key management. In a production environment, ensure proper security measures are implemented for handling sensitive information. 