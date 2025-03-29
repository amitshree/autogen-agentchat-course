import streamlit as st
import asyncio
from agent import get_code_explanation, get_code_optimization

# Streamlit UI
st.title("💡 AI Code Explainer & Debugger")
st.write("Upload a Python file or paste your code below to get AI-powered explanations and debugging insights.")

# File Upload or Text Input
uploaded_file = st.file_uploader("Upload a Python file", type=["py"])
code_input = st.text_area("Or paste your Python code here:", height=200)

# Process when "Send" button is clicked
if st.button("🚀 Send"):
    if uploaded_file:
        code = uploaded_file.read().decode("utf-8")
    elif code_input:
        code = code_input
    else:
        st.warning("⚠️ Please upload a file or enter code before clicking 'Send'.")
        st.stop()

    st.subheader("📖 Code Explanation")
    with st.spinner("🔍 Analyzing code... Please wait."):
        # Code Explanation
        explanation = asyncio.run(get_code_explanation(code))
        st.markdown(f"{explanation}")

    # Optimization Suggestions
    st.subheader("🚀 Optimization Suggestions")
    with st.spinner("✨ Optimizing code... Please wait."):
        optimized_code = asyncio.run(get_code_optimization(code))
        st.markdown(f"n{optimized_code}\n")
