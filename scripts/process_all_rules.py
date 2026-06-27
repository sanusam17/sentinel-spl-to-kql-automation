from pathlib import Path
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

spl_folder = Path("spl-rules")
kql_folder = Path("kql-rules")

kql_folder.mkdir(exist_ok=True)

for spl_file in spl_folder.glob("*.spl"):

    output_file = kql_folder / f"{spl_file.stem}.kql"

    print(f"Checking {spl_file.name}")

    # Skip if already converted and source file has not changed
    if (
        output_file.exists()
        and output_file.stat().st_mtime >= spl_file.stat().st_mtime
    ):
        print(f"Skipping {spl_file.name}")
        continue

    spl_query = spl_file.read_text()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Convert this SPL query to KQL:\n\n{spl_query}"
    )

    output_file.write_text(response.text)

    print(f"Generated {output_file}")