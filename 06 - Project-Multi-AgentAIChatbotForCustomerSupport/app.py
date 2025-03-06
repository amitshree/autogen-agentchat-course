import streamlit as st
import requests

# Streamlit UI Configuration
st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("💬 Multi-Agent AI Chatbot for Customer Support")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input field
if user_input := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process user query with chatbot
    with st.spinner("Processing..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat/", 
                json={"query": user_input},  # Ensure correct JSON format
                headers={"Content-Type": "application/json"},  # Explicitly set header
                timeout=10  # Prevent long hangs
            )

            if response.status_code == 200:
                bot_response = response.json()["response"]
            else:
                bot_response = f"Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            bot_response = f"Error: Unable to connect to the chatbot server.\n{str(e)}"

        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
