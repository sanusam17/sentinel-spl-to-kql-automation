from pathlib import Path
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

kql_folder = Path("kql-rules")
arm_folder = Path("arm-templates")

arm_folder.mkdir(exist_ok=True)

prompt_template = Path(
    "prompts/kql_to_arm_prompt.txt"
).read_text(
    encoding="utf-8"
)

for kql_file in kql_folder.glob("*.kql"):

    output_file = (
        arm_folder /
        f"{kql_file.stem}.json"
    )

    print(
        f"Checking {kql_file.name}"
    )

    # Skip if ARM template already exists
    if output_file.exists():
        print(
            f"Skipping {kql_file.name}"
        )
        continue

    print(
        f"Generating ARM for {kql_file.stem}"
    )

    kql_query = kql_file.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.format(
        kql_query=kql_query
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    arm_json = response.text.strip()

    if arm_json.startswith("```json"):
        arm_json = arm_json.replace(
            "```json",
            ""
        )

    arm_json = arm_json.replace(
        "```",
        ""
    ).strip()

    output_file.write_text(
        arm_json,
        encoding="utf-8"
    )

    print(
        f"Generated {output_file}"
    )

print(
    "ARM template generation complete"
)