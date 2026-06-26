import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text.strip()
