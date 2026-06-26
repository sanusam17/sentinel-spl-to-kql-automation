import os
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

with open("kql-rules/rule.kql", "r") as f:
    kql_query = f.read()

prompt = f"""
Convert the following Microsoft Sentinel KQL query into a valid
Microsoft Sentinel Scheduled Analytics Rule ARM template.

Return only JSON.

KQL:

{kql_query}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

with open("arm-templates/rule.json", "w") as f:
    f.write(response.text)

print("ARM template generated successfully")