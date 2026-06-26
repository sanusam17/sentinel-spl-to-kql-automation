import os
from pathlib import Path
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

prompt_template = Path(
    "prompts/spl_to_kql.txt"
).read_text()

# Ensure output directory exists
Path("kql-rules").mkdir(
    parents=True,
    exist_ok=True
)

for spl_file in Path("spl-rules").glob("*.spl"):

    rule_name = spl_file.stem

    print(f"Processing {rule_name}")

    spl_query = spl_file.read_text()

    prompt = prompt_template.replace(
        "{SPL_QUERY}",
        spl_query
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    output_file = Path(
        f"kql-rules/{rule_name}.kql"
    )

    output_file.write_text(response.text)

    print(f"Generated {output_file}")