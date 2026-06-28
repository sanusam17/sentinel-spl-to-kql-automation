from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors

import os
import json
import uuid
import copy
import time

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

VALID_SEVERITIES = {
    "High",
    "Medium",
    "Low",
    "Informational"
}

VALID_TACTICS = {
    "Reconnaissance",
    "ResourceDevelopment",
    "InitialAccess",
    "Execution",
    "Persistence",
    "PrivilegeEscalation",
    "DefenseEvasion",
    "CredentialAccess",
    "Discovery",
    "LateralMovement",
    "Collection",
    "CommandAndControl",
    "Exfiltration",
    "Impact"
}

TACTIC_MAP = {
    "Initial Access": "InitialAccess",
    "Defense Evasion": "DefenseEvasion",
    "Privilege Escalation": "PrivilegeEscalation",
    "Credential Access": "CredentialAccess",
    "Lateral Movement": "LateralMovement",
    "Command and Control": "CommandAndControl",
    "Resource Development": "ResourceDevelopment"
}
# Determine files to process

changed_file_path = Path(
    "changed_files.txt"
)

if changed_file_path.exists():

    print(
        "Using changed_files.txt"
    )

    changed_files = (
        changed_file_path
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    kql_files = []

    for spl_path in changed_files:

        spl_file = Path(
            spl_path
        )

        kql_file = (
            kql_folder /
            f"{spl_file.stem}.kql"
        )

        if kql_file.exists():

            kql_files.append(
                kql_file
            )

    if not kql_files:

        print(
            "No changed KQL files found."
        )

        exit(0)

else:

    print(
        "changed_files.txt not found. "
        "Processing all KQL files."
    )

    kql_files = list(
        kql_folder.glob("*.kql")
    )

# Process files

for kql_file in kql_files:

    print(
        f"Generating ARM for {kql_file.stem}"
    )

    output_file = (
        arm_folder /
        f"{kql_file.stem}.json"
    )

    kql_query = kql_file.read_text(
        encoding="utf-8"
    )

    prompt = prompt_template.replace(
        "{kql_query}",
        kql_query
    )

    response = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            break

        except errors.APIError as e:

            print(
                f"Attempt {attempt + 1}/3 failed "
                f"for {kql_file.name}: {e}"
            )

            wait_time = (
                20 * (attempt + 1)
            )

            print(
                f"Waiting {wait_time} seconds..."
            )

            time.sleep(
                wait_time
            )

    if response is None:

        print(
            f"Failed to process "
            f"{kql_file.name}"
        )

        continue

    metadata_text = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        metadata = json.loads(
            metadata_text
        )

    except Exception as e:

        print(
            f"JSON Parse Error "
            f"for {kql_file.name}: {e}"
        )

        continue

    arm = copy.deepcopy(
        master_template
    )

    resource = arm["resources"][0]

    props = resource["properties"]

    rule_guid = str(
    uuid.uuid5(
        uuid.NAMESPACE_DNS,
        kql_file.stem
    )
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

    severity = metadata.get(
        "severity",
        "Medium"
    )

    if severity not in VALID_SEVERITIES:
        severity = "Medium"

    props["severity"] = severity
    props["query"] = kql_query

    props["queryFrequency"] = metadata.get(
        "queryFrequency",
        "PT1H"
    )

    props["queryPeriod"] = metadata.get(
        "queryPeriod",
        "PT1H"
    )
    props["triggerThreshold"] = metadata.get(
    "triggerThreshold",
    0
    )

    raw_tactics = metadata.get(
        "tactics",
        []
    )

    normalized_tactics = [
        TACTIC_MAP.get(t, t)
        for t in raw_tactics
    ]

    invalid_tactics = [
        t for t in normalized_tactics
        if t not in VALID_TACTICS
    ]

    if invalid_tactics:
        print(
            f"Invalid tactics in "
            f"{kql_file.name}: "
            f"{invalid_tactics}"
        )
        continue

    props["tactics"] = normalized_tactics

    techniques = metadata.get(
    "techniques",
        []
    )

    if not isinstance(techniques, list):
        techniques = []

    props["techniques"] = techniques

    props["entityMappings"] = None

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