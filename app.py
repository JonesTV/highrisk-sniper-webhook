from flask import Flask, request, jsonify
from high_risk_sniper import should_snipe
from send_to_nova import send_to_nova

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    try:
        data = request.get_json(force=True)
        print(f"\n📦 Webhook received. Type: {type(data)}")
        print(f"📨 Full webhook payload:\n{data}\n")

        # Handle list or dict with 'transactions'
        if isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]
        elif isinstance(data, list):
            transactions = data
        else:
            print(f"[x] Unexpected root payload format: {type(data)} — {data}")
            return jsonify({"error": "Invalid webhook format"}), 400

        # Flatten nested lists
        flat_transactions = []
        for item in transactions:
            if isinstance(item, list):
                print("[⚠️] Nested list found, flattening.")
                flat_transactions.extend(item)
            else:
                flat_transactions.append(item)

        transactions = flat_transactions

        if not isinstance(transactions, list):
            print(f"[x] Transactions is not a list: {transactions}")
            return jsonify({"error": "Transactions must be a list"}), 400

        print(f"🔍 Total transactions after flatten: {len(transactions)}")

        for i, tx in enumerate(transactions):
            print(f"\n--- Transaction {i+1} ---")
            print(f"🔎 Type of tx: {type(tx)}")
            print(f"🔎 Transaction data: {tx}")

            if not isinstance(tx, dict):
                print(f"[x] Skipping non-dict transaction.")
                continue

            token_address = extract_token_address(tx)
            print(f"🔍 Extracted token address: {token_address}")

            if token_address and should_snipe(token_address):
                print(f"[✔] Sniping {token_address}")
                try:
                    send_to_nova(token_address)
                except Exception as e:
                    print(f"[x] Failed to send to Nova: {e}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"[🔥] Webhook handler crashed: {e}")
        return jsonify({"error": str(e)}), 500


def extract_token_address(tx):
    if not isinstance(tx, dict):
        print(f"[x] Non-dict transaction passed to extractor: {tx}")
        return None

    try:
        events = tx.get("events", {})
        if not isinstance(events, dict):
            print(f"[x] Unexpected events format: {events}")
            return None

        tokens = events.get("token", [])
        if not isinstance(tokens, list):
            print(f"[x] Unexpected token format: {tokens}")
            return None

        for inst in tokens:
            if isinstance(inst, dict) and "mint" in inst:
                return inst["mint"]

    except Exception as e:
        print(f"[x] Exception in extract_token_address: {e}")

    return None


if __name__ == '__main__':
    app.run(debug=True)
