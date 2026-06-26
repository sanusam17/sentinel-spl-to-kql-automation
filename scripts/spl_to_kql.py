from pathlib import Path
from gemini_client import generate

prompt_template = open("prompts/spl_to_kql.txt").read()

for file in Path("spl-rules").glob("*.spl"):
    spl = file.read_text()

    prompt = prompt_template.replace("{{SPL}}", spl)

    kql = generate(prompt)

    output = Path("kql") / (file.stem + ".kql")
    output.write_text(kql)

    print(f"Generated KQL: {file.name}")