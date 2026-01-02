from flask import Flask, request
from flask_cors import CORS
import json

import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = Path("data/json_parm")
OUTPUT_FILE = Path(OUTPUT_DIR) / "scrape_params.json"


@app.route("/save", methods=["POST"])
def save():

    print("POST /save called")
    # print("Payload:", request.json)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(request.json, f, indent=2)

    print("Saved OK")
    return "Saved OK"


if __name__ == "__main__":
    app.run(debug=True)
