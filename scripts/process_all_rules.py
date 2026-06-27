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

    spl_query = spl_file.read_text()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Convert this SPL query to KQL:\n\n{spl_query}"
    )

    output_file = kql_folder / f"{spl_file.stem}.kql"

    output_file.write_text(response.text)

    print(f"Generated {output_file}")