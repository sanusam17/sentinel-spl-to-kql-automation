from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors
import os
import time

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

spl_folder = Path("spl-rules")
kql_folder = Path("kql-rules")

kql_folder.mkdir(exist_ok=True)

# Load prompt template

prompt_template = Path(
    "prompts/spl_to_kql.txt"
).read_text(
    encoding="utf-8"
)

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

    spl_files = [
        Path(file_path)
        for file_path in changed_files
        if Path(file_path).exists()
    ]

    if not spl_files:

        print(
            "No changed SPL files found."
        )

        exit(0)

else:

    print(
        "changed_files.txt not found. "
        "Processing all SPL files."
    )

    spl_files = list(
        spl_folder.glob("*.spl")
    )

# Process files

for spl_file in spl_files:

    print(
        f"Processing {spl_file.name}"
    )

    output_file = (
        kql_folder /
        f"{spl_file.stem}.kql"
    )

    spl_query = spl_file.read_text(
        encoding="utf-8"
    )

    # Use replace() instead of format()
    # to avoid issues with JSON braces in prompts

    prompt = prompt_template.replace(
        "{spl_query}",
        spl_query
    )

    response = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            break

        except errors.APIError as e:

            print(
                f"Attempt {attempt + 1}/3 failed "
                f"for {spl_file.name}: {e}"
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
            f"{spl_file.name}"
        )

        continue

    kql_text = (
        response.text
        .replace("```kql", "")
        .replace("```", "")
        .strip()
    )

    # Always overwrite existing KQL
    output_file.write_text(
        kql_text,
        encoding="utf-8"
    )

    print(
        f"Generated {output_file}"
    )

print(
    "SPL to KQL conversion complete"
)