import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

def generate(prompt: str) -> str:
    return model.generate_content(prompt).text.strip()