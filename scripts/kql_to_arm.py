from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors

import os
import json
import uuid
import copy

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

kql_folder = Path("kql-rules")
arm_folder = Path("arm-templates")

arm_folder.mkdir(exist_ok=True)

prompt_template = Path(
    "prompts/kql_to_metadata_prompt.txt"
).read_text(
    encoding="utf-8"
)

master_template = json.loads(
    Path(
        "templates/sentinel_master_template.json"
    ).read_text(
        encoding="utf-8"
    )
)

for kql_file in kql_folder.glob("*.kql"):

    output_file = (
        arm_folder /
        f"{kql_file.stem}.json"
    )

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

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    except errors.APIError as e:

        print(
            f"Gemini API Error: {e}"
        )

        continue

    metadata_text = response.text.strip()

    if metadata_text.startswith("```json"):

        metadata_text = metadata_text.replace(
            "```json",
            ""
        )

    metadata_text = metadata_text.replace(
        "```",
        ""
    ).strip()

    try:

        metadata = json.loads(
            metadata_text
        )

    except Exception as e:

        print(
            f"JSON Parse Error: {e}"
        )

        continue

    arm = copy.deepcopy(
        master_template
    )

    resource = arm["resources"][0]

    props = resource["properties"]

    rule_guid = str(
        uuid.uuid4()
    )

    resource["id"] = (
        "[concat(resourceId('Microsoft.OperationalInsights/workspaces/providers', "
        "parameters('workspace'), "
        "'Microsoft.SecurityInsights'),'/alertRules/"
        + rule_guid +
        "')]"
    )

    resource["name"] = (
        "[concat(parameters('workspace'),"
        "'/Microsoft.SecurityInsights/"
        + rule_guid +
        "')]"
    )

    props["displayName"] = metadata.get(
        "displayName",
        kql_file.stem
    )

    props["description"] = metadata.get(
        "description",
        ""
    )

    props["severity"] = metadata.get(
        "severity",
        "Medium"
    )

    props["query"] = kql_query

    props["queryFrequency"] = metadata.get(
        "queryFrequency",
        "PT5M"
    )

    props["queryPeriod"] = metadata.get(
        "queryPeriod",
        "PT5M"
    )

    props["tactics"] = metadata.get(
        "tactics",
        []
    )

    props["techniques"] = metadata.get(
        "techniques",
        []
    )

    props["entityMappings"] = metadata.get(
        "entityMappings",
        []
    )

    output_file.write_text(
        json.dumps(
            arm,
            indent=4
        ),
        encoding="utf-8"
    )

    print(
        f"Generated {output_file}"
    )

print(
    "ARM template generation complete"
)