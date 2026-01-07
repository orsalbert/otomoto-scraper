import os
import json
import subprocess
from pathlib import Path
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

project_root = Path.cwd().parent
output_dir = project_root / Path("data/json_parm")
output_file = output_dir / "config.json"

script_dir = project_root / Path("src")
scraper_script = script_dir / Path("run_scraper.py")


@app.route("/scrape", methods=["POST"])
def scrape():
    print("\n[FLASK] POST /scrape called")

    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(request.json, f, indent=2)

    print("\n[FLASK] Config saved")

    # Start scraper
    process = subprocess.Popen(
        ["python", str(scraper_script)],
        cwd=script_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "USE_TQDM": "0"},  # disable tqdm
    )

    print("\n[FLASK] Scraper started")

    # Stream scraper output to terminal
    for line in process.stdout:
        print(f"[SCRAPER] {line}", end="")

    return "Saved & scraper started", 200


if __name__ == "__main__":
    app.run(debug=True)
