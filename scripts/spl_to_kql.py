from google import genai

client = genai.Client(
    api_key="YOUR_GEMINI_API_KEY"
)

with open("spl-rules/rule.spl", "r") as f:
    spl_query = f.read()

prompt = f"""
You are a Microsoft Sentinel Engineer.

Convert the following Splunk SPL query to Microsoft Sentinel KQL.

Return ONLY KQL.

SPL:

{spl_query}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

kql = response.text

with open("kql-rules/rule.kql", "w") as f:
    f.write(kql)

print("KQL generated successfully")