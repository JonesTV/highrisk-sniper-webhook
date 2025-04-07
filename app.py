from flask import Flask, request, jsonify
from high_risk_sniper import should_snipe
from send_to_nova import send_to_nova

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    print("✅ DEPLOYED VERSION: v0.1.9 - THIS IS LIVE")  # <== Confirms redeployment

    try:
        data = request.get_json(force=True)
        print(f"📦 Webhook received. Type: {type(data)}")
        print(f"📨 Payload:\n{data}\n")

        # Determine structure
        if isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]
        elif isinstance(data, list):
            transactions = data
        else:
            print(f"[x] Unexpected root payload format: {type(data)}")
            return jsonify({"error": "Invalid webhook format"}), 400

        # Flatten nested lists
        flattened = []
        for item in transactions:
            if isinstance(item, list):
                print("[⚠️] Nested list detected, flattening.")
                flattened.extend(item)
            else:
                flattened.append(item)

        transactions = flattened

        if not isinstance(transactions, list):
            print(f"[x] Transactions is not a list after flatten: {transactions}")
            return jsonify({"error": "Transactions must be a list"}), 400

        print(f"🔍 Total transactions: {len(transactions)}")

        for i, tx in enumerate(transactions):
            print(f"\n--- Transaction {i+1} ---")
            print(f"🔎 Type: {type(tx)}")
            print(f"📦 Data: {tx}")

            if not isinstance(tx, dict):
                print(f"[x] Skipping non-dict transaction.")
                continue

            token_address = extract_token_address(tx)
            print(f"🎯 Token Address: {token_address}")

            if token_address and should_snipe(token_address):
                print(f"[🚀] Sniping {token_address}")
                try:
                    send_to_nova(token_address)
                except Exception as e:
                    print(f"[x] Nova error: {e}")

        return jsonify({"status": "received", "version": "v0.1.9"}), 200

    except Exception as e:
        print(f"[🔥] Webhook handler crashed: {e}")
        return jsonify({"error": str(e)}), 500


def extract_token_address(tx):
    if not isinstance(tx, dict):
        print(f"[x] extract_token_address received non-dict: {tx}")
        return None

    try:
        events = tx.get("events", {})
        if not isinstance(events, dict):
            print(f"[x] Invalid 'events' format: {events}")
            return None

        tokens = events.get("token", [])
        if not isinstance(tokens, list):
            print(f"[x] Invalid 'token' format: {tokens}")
            return None

        for inst in tokens:
            if isinstance(inst, dict) and "mint" in inst:
                return inst["mint"]

    except Exception as e:
        print(f"[x] Exception in extract_token_address: {e}")

    return None


if __name__ == '__main__':
    app.run(debug=True)
