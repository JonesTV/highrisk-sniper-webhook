from flask import Flask, request, jsonify
import os
from high_risk_sniper import should_snipe  # Your logic
from send_to_nova import send_to_nova  # Nova alert

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    try:
        data = request.get_json(force=True)  # ← properly indented
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

    except Exception as e:
        print(f"[x] Error handling webhook: {e}")
        return jsonify({"error": str(e)}), 500


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
