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

for spl_file in spl_folder.glob("*.spl"):

    output_file = (
        kql_folder /
        f"{spl_file.stem}.kql"
    )

    # Skip if KQL already exists
    if output_file.exists():
        print(
            f"Skipping {spl_file.name}"
        )
        continue

    print(
        f"Processing {spl_file.name}"
    )

    spl_query = spl_file.read_text(
        encoding="utf-8"
    )

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Convert this SPL query to KQL:\n\n{spl_query}"
        )

    except errors.APIError as e:

        print(
            f"Gemini API Error for {spl_file.name}: {e}"
        )

        # Retry once for temporary service issues
        if "503" in str(e):

            print(
                "Gemini service busy. Waiting 60 seconds before retry..."
            )

            time.sleep(60)

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Convert this SPL query to KQL:\n\n{spl_query}"
                )

            except Exception as retry_error:

                print(
                    f"Retry failed for {spl_file.name}: {retry_error}"
                )

                continue

        else:
            continue

    output_file.write_text(
        response.text,
        encoding="utf-8"
    )

    print(
        f"Generated {output_file}"
    )

print(
    "SPL to KQL conversion complete"
)