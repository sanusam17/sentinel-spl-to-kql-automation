from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

kql = open("kql-rules/rule.kql").read()

prompt = open(
    "prompts/kql_to_arm.txt"
).read()

response = client.responses.create(
    model="gpt-5",
    input=prompt.replace(
        "{{KQL_QUERY}}",
        kql
    )
)

arm = response.output_text

with open(
    "arm-templates/rule.json",
    "w"
) as f:
    f.write(arm)