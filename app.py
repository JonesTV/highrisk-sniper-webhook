from flask import Flask, request, jsonify
from high_risk_sniper import should_snipe
from send_to_nova import send_to_nova

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    try:
        data = request.get_json(force=True)
        print(f"📦 Webhook Raw Data Type: {type(data)}")

        # Handle both formats: dict with "transactions" or raw list
        if isinstance(data, list):
            transactions = data
        elif isinstance(data, dict):
            transactions = data.get("transactions", [])
        else:
            print(f"[x] Unexpected data type: {type(data)} - {data}")
            return jsonify({"error": "Invalid webhook format"}), 400

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
