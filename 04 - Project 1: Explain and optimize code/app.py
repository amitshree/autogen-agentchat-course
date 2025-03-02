import streamlit as st
import tempfile
import asyncio
import subprocess
from agent import get_code_explanation, get_code_optimization

# Streamlit UI
st.title("💡 AI Code Explainer & Debugger")
st.write("Upload a Python file or paste your code below to get AI-powered explanations and debugging insights.")

# File Upload or Text Input
uploaded_file = st.file_uploader("Upload a Python file", type=["py"])
code_input = st.text_area("Or paste your Python code here:", height=200)

# Function to run Pylint
def run_pylint(filepath):
    """Run pylint as a subprocess and capture output"""
    result = subprocess.run(["pylint", "--output-format=text", filepath], capture_output=True, text=True)
    return result.stdout

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

    # Debugging & Error Analysis
    st.subheader("🐞 Debugging & Error Analysis")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(code.encode("utf-8"))
        temp_file_path = temp_file.name

    pylint_errors = run_pylint(temp_file_path)
    st.markdown(f"n{pylint_errors if pylint_errors else 'No issues found.'}\n")

    # Optimization Suggestions
    st.subheader("🚀 Optimization Suggestions")
    with st.spinner("✨ Optimizing code... Please wait."):
        optimized_code = asyncio.run(get_code_optimization(code))
        st.markdown(f"n{optimized_code}\n")
