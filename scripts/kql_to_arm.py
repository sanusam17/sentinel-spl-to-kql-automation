from pathlib import Path
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(
    api_key=api_key
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

    output_file = arm_folder / f"{kql_file.stem}.json"


    # Skip if ARM already exists and KQL has not changed
    if (
        output_file.exists()
        and output_file.stat().st_mtime >= kql_file.stat().st_mtime
    ):
        print(f"Skipping {kql_file.name}")
        continue

    print(f"Generating ARM for {kql_file.stem}")

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

    # Remove markdown if Gemini returns it
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

    print(f"Generated {output_file}")

print("ARM template generation complete")