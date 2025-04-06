from flask import Flask, request, jsonify
import os
from high_risk_sniper import should_snipe  # Your existing logic
from high_risk_sniper_log_all import send_to_nova  # or wherever you handle Nova

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    return jsonify({"status": "Webhook received"})
    transactions = data.get("transactions", [])

    for tx in transactions:
        token_address = extract_token_address(tx)
        if token_address:
            print(f"[+] Token detected: {token_address}")
            if should_snipe(token_address):
                print(f"[✔] Sniping {token_address}")
                send_to_nova(token_address)
                # Optional: Telegram alert or Google Sheets log

    return jsonify({"status": "received"})


def extract_token_address(tx):
    try:
        for inst in tx.get("events", {}).get("token", []):
            if inst.get("mint"):
                return inst["mint"]
    except Exception as e:
        print(f"[x] Failed to extract token: {e}")
    return None


if __name__ == '__main__':
    app.run(debug=True)
