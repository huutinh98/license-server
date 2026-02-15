from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

KEY_FILE = "keys.json"

def load_keys():
    with open(KEY_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/check", methods=["POST"])
def check_key():
    data = request.json
    user_key = data.get("key")

    db = load_keys()
    today = datetime.now().date()

    for k in db["keys"]:
        if k["key"] == user_key:
            if k["status"] != "active":
                return jsonify({"status": "disabled"})

            if datetime.strptime(k["expires_at"], "%Y-%m-%d").date() < today:
                k["status"] = "expired"
                save_keys(db)
                return jsonify({"status": "expired"})

            if k["used"] >= k["max_uses"]:
                k["status"] = "used_up"
                save_keys(db)
                return jsonify({"status": "used_up"})

            k["used"] += 1
            save_keys(db)

            return jsonify({
                "status": "valid",
                "remaining_uses": k["max_uses"] - k["used"]
            })

    return jsonify({"status": "invalid"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
