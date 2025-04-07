from flask import Flask, request, jsonify
from high_risk_sniper import should_snipe
from send_to_nova import send_to_nova

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    try:
        data = request.get_json(force=True)
        print(f"📦 Webhook Data Type: {type(data)}")

        # Support both list-based and dict-based webhook payloads
        transactions = []
        if isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]
        elif isinstance(data, list):
            transactions = data
        else:
            print(f"[x] Unexpected webhook format: {type(data)}")
            return jsonify({"error": "Invalid webhook format"}), 400

        for tx in transactions:
            if not isinstance(tx, dict):
                print(f"[x] Skipping non-dict tx: {tx}")
                continue

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
        events = tx.get("events", {})
        tokens = events.get("token", [])
        if isinstance(tokens, list):
            for inst in tokens:
                if isinstance(inst, dict) and "mint" in inst:
                    return inst["mint"]
    except Exception as e:
        print(f"[x] Failed to extract token address: {e}")
    return None

if __name__ == '__main__':
    app.run(debug=True)
