# scripts/spl_to_kql.py

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

with open("spl-rules/rule.spl") as f:
    spl = f.read()

prompt = open("prompts/spl_to_kql.txt").read()

response = client.responses.create(
    model="gpt-5",
    input=prompt.replace(
        "{{SPL_QUERY}}",
        spl
    )
)

kql = response.output_text

with open("kql-rules/rule.kql", "w") as f:
    f.write(kql)