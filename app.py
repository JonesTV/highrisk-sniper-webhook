from flask import Flask, request, jsonify
import os
from high_risk_sniper import should_snipe  # Make sure this file exists and is Vercel-compatible
from ws_sniper_log_all import send_to_nova  # Make sure this file exists

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    try:
    data = request.get_json(force=True)
    transactions = data.get("transactions", [])

    for tx in transactions:
        token_address = extract_token_address(tx)
        if token_address:
            print(f"[+] Token detected: {token_address}")
            if should_snipe(token_address):
                print(f"[✔] Sniping {token_address}")
                try:
                    send_to_nova(token_address)
                except Exception as e:
                    print(f"[x] Failed to send to Nova: {e}")
    
    return jsonify({"status": "received"}), 200


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
