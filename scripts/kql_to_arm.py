from pathlib import Path
import json
from gemini_client import generate

PROMPT_TEMPLATE = open("prompts/kql_to_arm.txt").read()

KQL_DIR = Path("kql")
ARM_DIR = Path("arm")
ARM_DIR.mkdir(exist_ok=True)

for file in KQL_DIR.glob("*.kql"):
    kql = file.read_text()

    prompt = PROMPT_TEMPLATE.replace("{KQL_QUERY}", kql)

    response = generate(prompt)

    try:
        arm_json = json.loads(response)
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON generated for {file.name}")

    output_file = ARM_DIR / f"{file.stem}.json"
    output_file.write_text(json.dumps(arm_json, indent=2))

    print(f"ARM generated: {file.name}")