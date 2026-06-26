import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = f"""
Convert this Splunk SPL query to Microsoft Sentinel KQL.

Return ONLY the KQL query.

SPL:
{spl_query}
"""

response = model.generate_content(prompt)

print(response.text)