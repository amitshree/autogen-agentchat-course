import streamlit as st
import requests

st.set_page_config(page_title="AI Customer Support Chatbot", layout="wide")

st.title("🛍️ AI Customer Support Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = "🤖 AI" if message["role"] == "assistant" else "👤 You"
    with st.chat_message(role):
        st.markdown(message["content"])

query = st.chat_input("Type your question here...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("👤 You"):
        st.markdown(query)

    response = requests.post("http://127.0.0.1:8000/chat", json={"query": query}).json()
    bot_response = response.get("response", "Sorry, I couldn't process that request.")

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("🤖 AI"):
        st.markdown(bot_response)
