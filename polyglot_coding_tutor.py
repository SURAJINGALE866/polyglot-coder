import streamlit as st
import subprocess
import sys
from googletrans import Translator
import openai
import nest_asyncio
import asyncio

# Apply nest_asyncio to allow asyncio to run in Streamlit's event loop
nest_asyncio.apply()

# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="AI Polyglot Coding Tutor", page_icon="🤖", layout="wide")
st.title("🤖 AI Polyglot Coding Tutor")
st.write("Write your request in any language, get working code in Python/Java/C++/JS + explanations!")

# --- Set your OpenAI API key ---
openai.api_key = "YOUR_OPENAI_API_KEY"

translator = Translator()

# -------------------------------
# User settings
# -------------------------------
local_lang = st.selectbox("Choose your local language", ["mr", "hi", "en", "es"])
prog_lang = st.selectbox("Choose programming language", ["Python", "Java", "C++", "JavaScript"])
user_request = st.text_area("✍ Describe what you want the code to do in your language")

# -------------------------------
# Step 1: Translate user request to English for AI processing
# -------------------------------
if user_request:
    request_en = asyncio.run(translator.translate(user_request, src=local_lang, dest='en')).text

# -------------------------------
# Step 2: Generate Code via OpenAI
# -------------------------------
def generate_code(prompt, lang):
    code_prompt = f"""
    Generate a {lang} program based on this request:
    {prompt}
    Provide only the code, no explanations.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=code_prompt,
        max_tokens=500,
        temperature=0
    )
    return response.choices[0].text.strip()

if st.button("Generate Code"):
    if 'request_en' in locals():
        with st.spinner("Generating code..."):
            code = generate_code(request_en, prog_lang)
            st.subheader(f"🔹 Generated {prog_lang} Code:")
            st.code(code, language=prog_lang.lower())

            # -------------------------------
            # Step 3: Run code safely
            # -------------------------------
            output = ""
            error_msg = ""

            try:
                if prog_lang == "Python":
                    exec_globals = {}
                    exec(code, {}, exec_globals)
                    output = exec_globals.get("_result", "")
                elif prog_lang == "Java":
                    with open("Main.java", "w", encoding="utf-8") as f:
                        f.write(code)
                    subprocess.run(["javac", "Main.java"], check=True)
                    result = subprocess.run(["java", "Main"], capture_output=True, text=True)
                    output = result.stdout
                elif prog_lang == "C++":
                    with open("main.cpp", "w", encoding="utf-8") as f:
                        f.write(code)
                    subprocess.run(["g++", "main.cpp", "-o", "main"], check=True)
                    result = subprocess.run(["./main"], capture_output=True, text=True)
                    output = result.stdout
                elif prog_lang == "JavaScript":
                    with open("script.js", "w", encoding="utf-8") as f:
                        f.write(code)
                    result = subprocess.run(["node", "script.js"], capture_output=True, text=True)
                    output = result.stdout
            except subprocess.CalledProcessError as e:
                error_msg = asyncio.run(translator.translate(str(e), dest=local_lang)).text
            except Exception as e:
                error_msg = asyncio.run(translator.translate(str(e), dest=local_lang)).text

            st.subheader("🖥 Output:")
            st.write(output if output else "⚡ No output")

            if error_msg:
                st.subheader("❌ Error / Guidance:")
                st.error(error_msg)

            # -------------------------------
            # Step 4: AI Teaching & Explanation
            # -------------------------------
            st.subheader("📘 AI Explanation / Teaching Tip:")

            def generate_explanation(code_snippet, lang, user_language):
                expl_prompt = f"""
                Explain this {lang} code step by step for a beginner in simple words:
                {code_snippet}
                """
                resp = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=expl_prompt,
                    max_tokens=300,
                    temperature=0
                )
                explanation_en = resp.choices[0].text.strip()
                explanation_local = asyncio.run(translator.translate(explanation_en, dest=user_language)).text
                return explanation_local

            explanation = generate_explanation(code, prog_lang, local_lang)
            st.write(explanation)
