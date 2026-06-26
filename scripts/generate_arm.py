import os
from pathlib import Path
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

prompt_template = Path(
    "prompts/kql_to_arm.txt"
).read_text()

# Ensure output directory exists
Path("kql-rules").mkdir(
    parents=True,
    exist_ok=True
)

Path("arm-templates").mkdir(
    parents=True,
    exist_ok=True
)

for kql_file in Path("kql-rules").glob("*.kql"):

    rule_name = kql_file.stem

    print(
        f"Generating ARM {rule_name}"
    )

    kql_query = kql_file.read_text()

    prompt = prompt_template.replace(
        "{KQL_QUERY}",
        kql_query
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    output_file = Path(
        f"arm-templates/{rule_name}.json"
    )

    output_file.write_text(
        response.text
    )

    print(
        f"Generated {output_file}"
    )