import os
import json
import subprocess
from pathlib import Path
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

project_root = Path.cwd().parent
OUTPUT_DIR = project_root / Path("data/json_parm")
OUTPUT_FILE = OUTPUT_DIR / "config.json"

script_dir = project_root / Path("src")
SCRAPER_SCRIPT = script_dir / Path("run_scraper.py")


@app.route("/scrape", methods=["POST"])
def scrape():
    print("\n[FLASK] POST /scrape called")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(request.json, f, indent=2)

    print("\n[FLASK] Config saved")

    # 🔥 Start scraper
    process = subprocess.Popen(
        ["python", str(SCRAPER_SCRIPT)],
        cwd=script_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    print("\n[FLASK] Scraper started")

    # Stream scraper output to terminal
    for line in process.stdout:
        print(f"[SCRAPER] {line}", end="")

    return "Saved & scraper started", 200


if __name__ == "__main__":
    app.run(debug=True)
